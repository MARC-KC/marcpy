import keyring
import getpass
import pyodbc
import pandas

keyring.set_password("test", "test2", "test3")
keyring.set_password(":test:test2", "test2", "test3")
keyring.get_password("test", "test2")
keyring.get_password("git:https://github.com", "jacpete")
keyring.get_password(":CensusKey:", )


for item in keyring.get_keyring().get_preferred_collection().get_all_items():
    print(item.get_label(), item.get_attributes())

c = keyring.get_credential("test", None)
c.username

keyring.get_credential(":CensusKey:", None).username



keyring.set_password("test3", "test4", getpass.getpass())
keyring.get_password("test3", "test4")

keyring.set_password(":DB_MARC_DEV.marcpub:username", "username", getpass.getpass())
keyring.get_password(":DB_MARC_DEV.marcpub:username", "username")



#keyringR



# keyring.set_password(service_name=":DB_conn:MARC_PRD.marcdl", username="MARC_PRD.marcdl", password=getpass.getpass())
# keyring.get_password(service_name=":DB_conn:MARC_PRD.marcdl", username="MARC_PRD.marcdl")

# keyring.set_password(service_name=":DB_conn:MARC_PUB.marcpub", username="MARC_PUB.marcpub", password=getpass.getpass())
# keyring.get_password(service_name=":DB_conn:MARC_PUB.marcpub", username="MARC_PUB.marcpub")

# keyring.set_password(service_name=":DB_conn:MARC_DEV.marcpub", username="MARC_DEV.marcpub", password=getpass.getpass())
# keyring.get_password(service_name=":DB_conn:MARC_DEV.marcpub", username="MARC_DEV.marcpub")

# keyring.set_password(service_name=":DB_conn:MARC_DEV.marcdl", username="MARC_DEV.marcdl", password=getpass.getpass())
# keyring.get_password(service_name=":DB_conn:MARC_DEV.marcdl", username="MARC_DEV.marcdl")


import marcpy

marcpy.key_set(serviceName="DB_conn", userName="MARC_PRD.marcdl")
marcpy.key_get(serviceName="DB_conn", userName="MARC_PRD.marcdl")

marcpy.key_set(serviceName="DB_conn", userName="MARC_PUB.marcpub")
marcpy.key_get(serviceName="DB_conn", userName="MARC_PUB.marcpub")

marcpy.key_set(serviceName="DB_conn", userName="MARC_DEV.marcpub")
marcpy.key_get(serviceName="DB_conn", userName="MARC_DEV.marcpub")

marcpy.key_set(serviceName="DB_conn", userName="MARC_DEV.marcdl")
marcpy.key_get(serviceName="DB_conn", userName="MARC_DEV.marcdl")


# Driver={ODBC Driver 17 for SQL Server};Server=<serverName>;Database=<databaseName>;UID=<schemaName>;PWD=<password>;

# Driver={ODBC Driver 17 for SQL Server};Server=chiefs;Database=MARC_PUB;UID=marcpub;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=knights;Database=MARC_PRD;UID=marcdl;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=phantoms;Database=MARC_DEV;UID=marcpub;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=phantoms;Database=MARC_DEV;UID=marcdl;PWD=<password>;

# databaseString = "MARC_PRD.marcdl"
def connectODBC(databaseString):

    #Create Service Name
    serviceName = ":DB_conn:" + databaseString

    #Check that the key exists
    try:
        keyring.get_credential(serviceName, None).username
    except AttributeError:
        print("Cannot find a record for " + databaseString + " in your Windows Credential Manager. Does it need added?")
        print("See instructions HERE on how to add it.")
        raise

    connString = keyring.get_password(serviceName, databaseString)

    # print(connString)

    conn = pyodbc.connect(connString)

    return conn

connectODBC("MARC_PRD.marcdl")
connectODBC("MARC_PRD.marcdl2")

MARC_PRD_marcdl_conn = connectODBC("MARC_PRD.marcdl")

sql = "SELECT * FROM CovidCaseDeathTest"
test = pandas.read_sql(sql, MARC_PRD_marcdl_conn)

sql = "SELECT * FROM CovidHospitalTeletracking"
test2 = pandas.read_sql(sql, MARC_PRD_marcdl_conn)



#The R in 'getR' is in reference that this function is compliant with the service name formats used by R's implementation of the Keyring package. 
# Creating and getting keys with these functions makes sure that the keys can be used by both Python and R

def _key_create_serviceName(serviceName="", userName=""):
    """Creates the service name string from the inputs
    
    The created serviveName is compliant with R's keyring package that requires
    the service to be formatted like ":<service>:<username>. These are just 
    helpers to make coding that in Python more user friendly and to allow R
    and Python to share keys stored in Windows credential manager.
    This function is used internally.

    Parameters
    ----------
    serviceName : str 
        The service name for the keyring object you are working with.
    userName : str
        The username for the keyring object you are woking with.

    Returns
    -------
    str
        A formatted serviceName string is returned.
    """

    #Create R Compliant Service Name
    serviceName = ":" + serviceName + ":" + userName

    if serviceName == "::":
        raise RuntimeError("Both serviceName and userName cannot be left blank.")
    
    return serviceName




def key_get(serviceName="", userName=""):
    """Retrieves a key password
    
    Given the serviceName and userName, this function will retrieve the password
    for the specified key. This is a wrapper around keyring.get_password() to 
    work with R compliant keys saved in the Windows Credential Manager.

    Parameters
    ----------
    serviceName : str 
        The service name for the keyring object you want to retrieve.
    userName : str
        The username for the keyring object you want to retrieve.

    Returns
    -------
    str
        The saved password for the specified key.
    """

    #Create R Compliant Service Name
    serviceName = _key_create_serviceName(serviceName, userName)

    #Check that the key exists
    try:
        keyring.get_credential(serviceName, None).username
    except AttributeError:
        print("Cannot find a record for " + userName + " in your Windows Credential Manager. Does it need added?")
        print("See instructions HERE on how to add it.")
        raise
    
    #Retrieve Key
    outPass = keyring.get_password(serviceName, userName)
    
    return outPass






def key_set(serviceName="", userName=""):
    """Sets a key password
    
    Given the serviceName and userName, this function will set the password
    for the specified key. When called it will provide a prompt in 
    the console/REPL. Nothing will show that you type your pasword into that 
    prompt (like linux command line passwords), but pressing enter will save 
    what was typed. This is a wrapper around keyring.set_password() to 
    work with R compliant keys saved in the Windows Credential Manager.

    Parameters
    ----------
    serviceName : str 
        The service name for the keyring object you want to set.
    userName : str
        The username for the keyring object you want to set.

    Returns
    -------
    None
        The function has no return value
    """

    #Create R Compliant Service Name
    serviceName = _key_create_serviceName(serviceName, userName)

    #Check that the key doesn't exist
    keyPass = keyring.get_password(serviceName, userName)
    if keyPass is not None:
        raise RuntimeError("There is already a key set for " + serviceName + ". Please delete the old key and reset it if you need to alter it.")

    #Set Key
    keyring.set_password(serviceName, userName, getpass.getpass())


def key_delete(serviceName="", userName=""):
    """Deletes a key password
    
    Given the serviceName and userName, this function will delete the specified
    key form the Windows Credential Manager. This is a wrapper around 
    keyring.delete_password() to work with R compliant keys saved in the 
    Windows Credential Manager.

    Parameters
    ----------
    serviceName : str 
        The service name for the keyring object you want to delete.
    userName : str
        The username for the keyring object you want to delete.

    Returns
    -------
    None
        The function has no return value
    """

    #Create R Compliant Service Name
    serviceName = _key_create_serviceName(serviceName, userName)

    #Check that the key exists
    try:
        keyring.get_credential(serviceName, None).username
    except AttributeError:
        print("Cannot find a record for " + userName + " in your Windows Credential Manager. Check your inputs")
        raise

    #Delete key
    keyring.delete_password(serviceName, userName)




_key_create_serviceName("CENSUS_KEY", "")

key_set("CENSUS_KEY")
key_get("CENSUS_KEY")
key_delete("CENSUS_KEY")

key_set("CENSUS_KEY", "")
key_get("CENSUS_KEY", "")
key_delete("CENSUS_KEY", "")
