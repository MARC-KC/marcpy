"""This module holds helper functions for working with SQL tables. These 
functions may be hardcoded to work with Microsoft SQL Servers as that is what
MARC uses.
"""
import datetime
import urllib.parse
import re

import pyodbc
import sqlalchemy
from marcpy import keyring_wrappers
import numpy
import pandas

# databaseString = "chiefs.marc_pub.marcpub"
def connectODBC(databaseString):
    """Connect to ODBC Database Using keyring
    
    Creates connection to ODBC database with {pyobdc} using the data contained 
    in keyrings. This is generally used for internal purposes at MARC to make 
    database connections a lazier and safer proccess with {keyring}. See 
    documentation at ### to set up database connection keys.
    
    Parameters
    ----------
    databaseString : str 
        The username for the keyring object you are wanting to connect to. In 
        the format of '<DB_Name>.<Schema>'.
    
    Returns
    -------
    dictionary
        Contains a dictionary with the following elements:
            'pyodbc' - pyodbc.Connection - A {pyodbc} connection object for the 
                SQL Database.
            'sqlalchemy' - sqlalchemy.engine - An odbc based connection string 
                object for connections to the SQL Database using {sqlalchemy}.
            'details' - dictionary - holds plain text connection details. Has 
                the keys: 'Driver', 'Server', 'Database', 'UID', and 'PWD'
    """
    
    #Create Service Name
    serviceName = ":DB_conn:" + databaseString
    
    #Retrieve database connection string
    connString = keyring_wrappers.key_get("DB_conn", databaseString)
    
    #Parse string into details dictionary.
    lst_details = [{x.split("=", 1)[0] : x.split("=", 1)[1]} for x in connString.split(";")[0:-1]]
    details = dict((key, d[key]) for d in lst_details for key in d)
    
    #Create pyodbc database connection.
    conn = pyodbc.connect(connString)
    
    #Create sqlalchemy engine connection
    quotedConnString = urllib.parse.quote_plus(connString)
    engine = sqlalchemy.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quotedConnString))
    
    #Create return dictionary
    out = {'pyodbc':conn, 'sqlalchemy':engine, 'details':details}
    
    return out



def _pandas_type_checker(type_in):
    """Convert types to pandas types
    
    Uses a dictionary to return a compatible {pandas} datatype given a type 
    input. This serves as an internal helper function for higher level 
    functions in marcpy.
    
    Parameters
    ----------
    type_in : type
        The type you want to convert to a pandas type.
    
    Return
    ------
    pandas type
        A {pandas} compatible datatype. If the supplied type_in is not managed
        in the type dictionary it will return None. If you come across this, you
        can edit the dictionary in the function to handle the new type.
    """
    
    switchDict = {
        bool: "boolean",
        int: "Int64",
        float: "Float64",
        str: "string",
        datetime.date: pandas.DatetimeTZDtype,
        datetime.datetime: pandas.DatetimeTZDtype
    }
    
    pandasType = switchDict.get(type_in, None)    
    return pandasType



def getOBDCtable(conn, query):
    """Get a {pandas} dataframe from the {pyodbc} connection
    
    This function is a more explicit implimentation of `pandas.read_sql()` when
    working in an MSsql database. It builds up a dataframe using only the data
    returned by the {pyodbc} cursor object. It was created so that columns get 
    correctly typed without coercing too soon. The `pandas.read_sql()` function
    defaults to the old {pandas} types prior to 1.0 (when the pandas.na) was 
    introduced for backwards compatibility. This is made to correctly type 
    data according to the new specifications.
    
    Parameters
    ----------
    conn : pyodbc.Connection
        A {pyodbc} connection object for the SQL Database.
    query : str
        SQL Query to server to request table
        
    Return
    ------
    dataframe
        A pandas dataframe with the query results.
    """
    
    #Read from Database
    cursor = conn.cursor()
    cursor.execute(query)
    names = [column[0] for column in cursor.description]
    types = [column[1] for column in cursor.description]
    nulls = [column[6] for column in cursor.description]
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()


    #Get Pandas types
    pandasTypes = list(map(_pandas_type_checker, types))

    #Make sure all types are managed by pandas_type_checker
    if any(map(lambda x: x == None, pandasTypes)):
        unmanagedIDs = numpy.where(numpy.array(list(map(lambda x: x == None, pandasTypes))))[0]
        unmanagedNames = numpy.array(names)[unmanagedIDs]
        unmanagedTypes = numpy.array(types)[unmanagedIDs]
        message = "The following column(s) ['" + "', '".join(unmanagedNames) + "'] have the following unmanaged datatype(s) ['" + "', '".join(unmanagedTypes) + "'] for conversion to a pandas DataFrame."
        message = message + "\nPlease edit `marcpy.pandas_type_checker()` to handle the unmanaged datatype(s)."
        raise RuntimeError(message)


    #Create from series
    outSeries = [None] * len(names)
    for i in range(0,len(names)):
        colData = list(map(lambda x: x[i], rows))
        colName = names[i]
        colType = types[i]
        colNull = nulls[i]
        pandasType = pandasTypes[i]
        outSeries[i] = pandas.Series(data = colData, dtype = pandasType, name = colName)

    outPdf = pandas.concat(outSeries, axis = 1)

    return outPdf



def dbListSchemas(conn, rmSchemaRegex = ["sys", "sde", "^INFORMATION_SCHEMA$", "^db_\\.*"]):
    """List all schema in database
    
    Searches schema in in the INFORMATION_SCHEMA.SCHEMATA table.
    Confirmed only to work with MS-SQL databases.
    
    Parameters
    ----------
    conn : sqlalchemy.Engine
        A sqlalchemy engine connection to use with pandas.read_sql()
    rmSchemaRegex : list or None
        List of characters containing schema regex to avoid searching
        (removed schema regex). Ignores some default system level schema and schema
        only used by the ESRI SDE bindings that don't actually contain user created
        tables.
    
    Return
    ------
    pandas.Series 
        A pandas series of schemas at the connection.
    """
    
    all_schema = pandas.read_sql("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA", conn)['SCHEMA_NAME']
    
    if rmSchemaRegex is None or len(rmSchemaRegex) == 0:
        out = all_schema
    else:
        out = all_schema[~all_schema.apply(lambda x: bool(re.search("|".join(rmSchemaRegex), x)))]
    
    return out


def dbTableStructure(conn, addGeoIndicator = False, includeViews = True, rmTableRegex = ["^[a-zA-Z]\d+$", "^SDE_"], rmSchemaRegex = ["sde"]):
    """List all tables in a database
    
    Searches tables in in the INFORMATION_SCHEMA.TABLES table. This functions 
    also pairs each table with its schema and can handle checking if the table 
    has spatial data and identify if it is a view.
    Confirmed only to work with MS-SQL databases.
    
    Parameters
    ----------
    conn : sqlalchemy.Engine
        A sqlalchemy engine connection to use with pandas.read_sql()
    addGeoIndicator : boolean
        Should the `isSpatial` column be exported? Default is FALSE.
    includeViews : boolean
        Should output included views?
    rmTableRegex : list or None
        List of strings containing table name regex to avoid
        searching (removed table regex). Ignores some tables that are only used by
        the ESRI SDE bindings that don't actually contain user created data.
    rmSchemaRegex : list or None
        List of strings containing schema regex to avoid searching
        (removed schema regex). Ignores some default system level schema and schema
        only used by the ESRI SDE bindings that don't actually contain user created
        tables.
    
    Return
    ------
    pandas.Dataframe
        A pandas dataframe with a row for each table in the database connection.
        Contains 4 or 5 columns ('Database', 'Schema', 'Table', 'isView', and 
        optionally 'isSpatial'). The return dataframe can then easily be 
        searched, filtered, and queried to find the tables you were looking for.
    """
    
    tables = pandas.read_sql("SELECT * FROM INFORMATION_SCHEMA.TABLES", conn)
    
    #Filter data
    if rmTableRegex is not None and len(rmTableRegex) != 0:
        tables = tables.loc[~tables['TABLE_NAME'].apply(lambda x: bool(re.search("|".join(rmTableRegex), x)))]
    
    if rmSchemaRegex is not None and len(rmSchemaRegex) != 0:
        tables = tables.loc[~tables['TABLE_SCHEMA'].apply(lambda x: bool(re.search("|".join(rmSchemaRegex), x)))]
    
    #Add Spatial Indicator
    if addGeoIndicator:
        def _isGeo(row):
            sqlQuery =  """ SELECT * 
                            FROM INFORMATION_SCHEMA.COLUMNS 
                            WHERE TABLE_SCHEMA = '{schema}' AND TABLE_NAME = '{table}' AND (DATA_TYPE = 'geometry' OR DATA_TYPE = 'geography')
                        """.format(schema = row['TABLE_SCHEMA'], table = row['TABLE_NAME'])
            return pandas.read_sql(sqlQuery, conn).shape[0] > 0
        
        tables['isSpatial'] = tables.apply(_isGeo, axis = 1)
    
    #Rename Columns
    tables = tables.rename(columns = {'TABLE_CATALOG':'Database', 'TABLE_SCHEMA':'Schema', 'TABLE_NAME':'Table', 'TABLE_TYPE':'isView'})
    
    #Handle Views Column
    tables['isView'] = tables['isView'] == 'VIEW'
    if not includeViews:
        tables = tables[~tables['isView']]
    
    return tables

