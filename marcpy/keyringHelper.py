import getpass

import keyring
import pyodbc


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

