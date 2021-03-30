"""This module holds helper functions for setting up and managing Git and 
GitHub credentials.
"""

import getpass
import os
import subprocess
import webbrowser

import keyring

from marcpy.utils import query_yesNo



def __resolve_gitBashExe(gitBashExe=""):
    """Checks existance of the supplied git-bash executable path
    
    If gitBashExe is left as an empty string, common file locations will be 
    searched until a path is found or the function produces a RuntimeError.
    This function is used internally.

    Parameters
    ----------
    gitBashExe : str 
        The Git-Base executable path. Defaults to the searching in common file
        locations.

    Returns
    -------
    str
        Returns the checked or resolved Git-Bash executable file path.
    """

    #Check that gitBashExe is not empty and try to search for it in predefined locations
    if gitBashExe == "":
        potentialPaths = [os.path.join(os.environ.get('PROGRAMFILES'), 'Git', 'bin', 'bash.exe')]
        for pth in potentialPaths:
            if os.path.exists(pth):
                gitBashExe = pth
                break
        if gitBashExe == "":
            raise RuntimeError("Could not find the path for git-bash. Please specify it explicitly.")
    else:
        if not os.path.exists(gitBashExe):
            raise RuntimeError("The path provided for git-bash does not exist. Please check the filepath is correct.")

    return gitBashExe

# __resolve_gitBashExe()



def getGitConfig(gitBashExe = ""):
    """Retrieve the global git config values for user.name and user.email  
    
    Checks to see if the user.name and user.email are set in your Git config 
    files and returns the values in a list or errors trying.

    Parameters
    ----------
    gitBashExe : str 
        The Git-Base executable path. Defaults to the searching in common file
        locations.

    Returns
    -------
    dictionary
        Returns a dictionary object with the values for user.name and 
        user.email.
    """

    #Check git-bash exe
    gitBashExe = __resolve_gitBashExe(gitBashExe)

    #Get Username
    usernameCommand = "git config user.name"
    try:
        username = subprocess.check_output([gitBashExe, '-c', usernameCommand]).decode("utf-8").rstrip('\n')
        if (username == ""):
            raise RuntimeError("")
    except:
        raise RuntimeError("The user.name key is not set for the git config. It must be set in order to return it.")

    #Get Email
    emailCommand = "git config user.email"
    try:
        email = subprocess.check_output([gitBashExe, '-c', emailCommand]).decode("utf-8").rstrip('\n')
        if (email == ""):
            raise RuntimeError("")
    except:
        raise RuntimeError("The user.email key is not set for the git config. It must be set in order to return it.")

    #Create output
    output = {'username': username, 'email': email}

    return output


# getGitConfig()


def setGitConfig(username, email, gitBashExe = ""):
    """Set the global git config values for user.name and user.email  
    
    Checks to see if the user.name and user.email are set in your Git config 
    files and attempts to set/reset the values given the function input.

    Parameters
    ----------
    username : str
        The username of your GitHub account.
    email : str
        The email used for your GitHub account (Preferably your MARC email).
    gitBashExe : str 
        The Git-Base executable path. Defaults to the searching in common file
        locations.

    Returns
    -------
    None
        Nothing is returned
    """

    #Check git-bash exe
    gitBashExe = __resolve_gitBashExe(gitBashExe)

    #Check for current config
    try:
        currentConfig = getGitConfig()
    except RuntimeError:
        print("Creating a new key...")
        currentConfig = None
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise
    
    #Check for overwrite permission.
    if currentConfig is not None:
        print("Git is already configured with user.name='" + currentConfig['username'] + "' and user.email='" + currentConfig['email'] + "'.")
        if query_yesNo("Do you want to overwrite the current values") == 'n':
            return None
        else:
            print("Creating a new key...")
    
    #Set the Values using subprocess commands
    usernameCommand = 'git config --global user.name "' + username + '"'
    emailCommand = 'git config --global user.email "' + email + '"'
    subprocess.run([gitBashExe, '-c', usernameCommand])
    subprocess.run([gitBashExe, '-c', emailCommand])

    return None
    
# setGitConfig('jacpete', "jpeterson@marc.org")


def gitcreds_get():
    """Retrieve GitHub logon credentials with {keyring}.
    
    Searches for the existance of the predefined service name in Windows 
    Credential Manager and retrieves the password.

    Returns
    -------
    str
        GitHub logon password.
    """

    serviceName = "git:https://github.com"

    #Check for current record
    if keyring.get_credential(serviceName, None) is None:
        raise RuntimeError("Cannot find any saved git credentials in your Windows Credential Manager. Does it need added? See instructions HERE on how to add it.")
    
    #Retrieve password
    userName = keyring.get_credential(serviceName, None).username
    passwd = keyring.get_password(serviceName, userName)

    return passwd

# gitcreds_get()



def gitcreds_set(userName=''):
    """Set GitHub logon credentials with {keyring}  
    
    Sets the GitHub login credentials that are used many applications that 
    connect to GitHub.

    Parameters
    ----------
    username : str
        The username of your GitHub account.

    Returns
    -------
    None
        Nothing is returned
    """

    serviceName = "git:https://github.com"

    #Check that a git credential record is not set.
    if keyring.get_credential(serviceName, None) is not None:
        raise RuntimeError("There is already a git credentials key set in your Windows Credential Manager. If it needs changed, delete it and recreate it.")

    #If userName is blank, search for the username saved in your Git config file.
    if userName == "":
        try:
            currentConfig = getGitConfig()
        except:
            currentConfig = None
        if currentConfig is None:
            raise RuntimeError("userName was not specified and has not been set in your global Git configuration. Set it with 'marcpy.gitcreds.setGitConfig()`.")
        else:
            userName = currentConfig['username']

    #Create the password.
    keyring.set_password(serviceName, userName, getpass.getpass(prompt="Enter PAT: "))

# gitcreds_set()
    
def gitcreds_delete():
    """Delete GitHub logon credentials with {keyring}  
    
    Deletes the GitHub login credentials from your Windows Credential Store.

    Returns
    -------
    None
        Nothing is returned
    """

    serviceName = "git:https://github.com"

    #Check for current record and delete if found
    if keyring.get_credential(serviceName, None) is None:
        print("A record for '" + serviceName + "' does not exist. No record deleted.")
    else:
        userName = keyring.get_credential(serviceName, None).username
        keyring.delete_password(serviceName, userName)
    
    return None



def gitcreds_createPAT(scopes = ['repo', 'user', 'gist', 'workflow'], description = "Python:GITHUB_PAT"):
    """Create a GitHub PAT
    
    This is a simplified port of the R function {usethis::create_github_token()}.

    Parameters
    ----------
    scopes : list
        Character vector of token scopes, pre-selected in the web form.
        Final choices are made in the GitHub form. Read more about GitHub API
        scopes at
        <https://docs.github.com/apps/building-oauth-apps/understanding-scopes-for-oauth-apps/>.
    description : str
        Short description or nickname for the token. You might
        (eventually) have multiple tokens on your GitHub account and a label can
        help you keep track of what each token is for.

    Returns
    -------
    None
        Nothing is returned
    """

    #Create URL
    url = "https://github.com/settings/tokens/new?scopes=" + ",".join(scopes) + "&description=" + description

    #Open URL in the default browser
    webbrowser.open_new(url)

    