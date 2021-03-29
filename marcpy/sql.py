"""This module holds helper functions for working with SQL tables. These 
functions may be hardcoded to work with Microsoft SQL Servers as that is what
MARC uses.
"""

import pyodbc
from marcpy import keyringHelper

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
    str
        A {pyodbc} connection object for the SQL Database.
    """

    #Create Service Name
    serviceName = ":DB_conn:" + databaseString

    #Retrieve database connection string
    connString = keyringHelper.key_get("DB_conn", databaseString)

    #Create database connection.
    conn = pyodbc.connect(connString)

    return conn
