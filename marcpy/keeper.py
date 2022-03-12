
import os
import sys
import subprocess
import re
import json


import pandas as pd
import numpy as np


def keeper_login(keeperExe = "C:\\Program Files (x86)\\Keeper Commander\\keeper-commander.exe"):
    """Calls the keeper CLI in a subprocess 
    
    Allows you to login and do the keeper setup without leaving your Python 
    shell.
    
    You must have the Keeper CLI installed. See documentation HERE 
    on how do temporarily give your CLI access to Keeper.
    
    Parameters
    ----------
    keeperExe : str
        The path to your local keeper-commander.exe installation. Defaults to
        "C:\\Program Files (x86)\\Keeper Commander\\keeper-commander.exe".
    
    Return
    ------
    None
    """
    
    subprocess.run('"{keeperExe}"'.format(keeperExe=keeperExe), shell = True)

def keeper_getKeyDF(keeperExe = "C:\\Program Files (x86)\\Keeper Commander\\keeper-commander.exe"):
    """Get a dataframe of all Keeper passwords associated with your account
    
    Uses the Keeper Commander CLI applicaiton to get a list of all Keeper 
    credentials (but not passwords) associated with your account.
    
    You must have the Keeper CLI installed and set up. See documentation HERE 
    on how do temporarily give your CLI access to Keeper.
    
    Parameters
    ----------
    keeperExe : str
        The path to your local keeper-commander.exe installation. Defaults to
        "C:\\Program Files (x86)\\Keeper Commander\\keeper-commander.exe".
    
    Return
    ------
    pandas.Dataframe
        A dataframe with the return from the list command in the Keeper CLI. It
        has  columns '#' - just and index, 'Record UID' - used to retrieve 
        passwords and edit records through the CLI, 'Type' - mainly unused by 
        MARC, 'Title' - title of the record (what we will use to search by to 
        retrieve record details), 'Login' - the username for the record, and 
        'URL' - part of the URL associated with the record (it gets cut off).
    """
    
    # Verify keeper EXE exists in specified location
    if not os.path.exists(keeperExe):
        raise RuntimeError("Verify Keeper Commander CLI is installed and the keeperExe path is correct.")
    
    # Use Keeper Commander CLI to retrive list of all keys
    sys.stdout.reconfigure(encoding='cp1252')
    command = '"{keeperExe}"  --batch-mode list'.format(keeperExe=keeperExe)
    keyList = subprocess.check_output(command, shell = True).decode("cp1252")
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Get column spacing information so data can be parsed
    spacingLine = re.findall("\\r\\n.*\\r\\n", keyList)[0]
    spacingLen = [len(x) + 2 for x in re.sub("\\r\\n", "", spacingLine).split("  ")]
    spacingLen[-1] = spacingLen[-1] - 2
    spacingIndex = [0] + list(np.array(spacingLen).cumsum())[:-1]
    
    # Split each line into columns and remove leading and trailing whitespace
    lineList = [x for x in keyList.split("\r\n") if x != '']
    columnList = [None] * len(lineList)
    for idx, line in enumerate(lineList):
        columnList[idx] = [re.sub('^\s*|\s*$', '', line[i:j]) for i,j in zip(spacingIndex, spacingIndex[1:]+[None])]
    
    #Create pandas dataframe and return
    keyDF = pd.DataFrame(columnList[2:], columns=columnList[0])
    return(keyDF)



def keeper_getKeyLogin(keyTitle, keyDF=None, keeperExe="C:\\Program Files (x86)\\Keeper Commander\\keeper-commander.exe"):
    """Get the username and password associated with a Keeper record
    
    Uses the Keeper Commander CLI applicaiton to get the password and username 
    of a record.
    
    You must have the Keeper CLI installed and set up. See documentation HERE 
    on how do temporarily give your CLI access to Keeper.
    
    Parameters
    ----------
    keyTitle : str
        The title of the Keeper record you are attempting to retrieve.
    keyDF : pandas.Dataframe
        The return from keeper_getKeyDF(). Default is None which calls 
        keeper_getKeyDF() internally.
    keeperExe : str
        The path to your local keeper-commander.exe installation. Defaults to
        "C:\\Program Files (x86)\\Keeper Commander\\keeper-commander.exe".
    
    Return
    ------
    Dict
        A dictionary with the 'record_uid', 'title', 'username', 'password', 
        'login_url', and 'notes' of the specified record.
    """
    
    #Create keyDF if None
    if keyDF is None:
        keyDF = keeper_getKeyDF(keeperExe)
    
    #Get Username and UID from keyDF
    if not keyDF['Title'].isin([keyTitle]).any():
        raise RuntimeError("The supplied 'keyTitle' does not match any titles in Keeper. Please check spelling.")
    UID = keyDF.loc[keyDF['Title'] == keyTitle, 'Record UID'].values[0]
    
    # Verify keeper EXE exists in specified location
    if not os.path.exists(keeperExe):
        raise RuntimeError("Verify Keeper Commander CLI is installed and the keeperExe path is correct.")
    
    # Retrieve details
    command = '"{keeperExe}" get --format=json {UID}'.format(keeperExe=keeperExe, UID=UID)
    details = json.loads(subprocess.check_output(command, shell = True).decode("cp1252"))
    
    return({'record_uid':UID, 'title':keyTitle, 'username':details.get('login', ''), 'password':details.get('password', ''), 'login_url':details.get('login_url', ''), 'notes':details.get('notes', '')})



def main(argv=None):
    keyDF = keeper_getKeyDF()
    
    keeper_getKeyLogin(keyTitle="Database_MARC_PUB_marcpub", keyDF=keyDF)



if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))



