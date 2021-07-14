"""This module holds helper functions for working with SQL tables. These 
functions may be hardcoded to work with Microsoft SQL Servers as that is what
MARC uses.
"""
import datetime
import urllib.parse

import pyodbc
import sqlalchemy
from marcpy import keyring_wrappers
import numpy
import pandas

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
    pyodbc.Connection
        A {pyodbc} connection object for the SQL Database.
    """
    
    #Create Service Name
    serviceName = ":DB_conn:" + databaseString
    
    #Retrieve database connection string
    connString = keyring_wrappers.key_get("DB_conn", databaseString)
    
    #Create pyodbc database connection.
    conn = pyodbc.connect(connString)
    
    #Create sqlalchemy engine connection
    quotedConnString = urllib.parse.quote_plus(connString)
    engine = sqlalchemy.create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quotedConnString))
    
    #Create return dictionary
    out = {'pyodbc':conn, 'sqlalchemy':engine}
    
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
