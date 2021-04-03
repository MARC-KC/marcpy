import os
import subprocess

import marcpy


newEnvLocation = "L:\\CondaEnvs\\test4"
envYML = "L:\\GitHub\\marcpy\\environment.yml"
# envYML = ""
cloneEnv = "marcRwebscraper" 
packages = ["test, test2"]
condaChannel = ""
pythonVersion = "3.7"
condaExe = os.environ.get('CONDA_EXE')

def _env_CreateOrClone(newEnvLocation, envYML = "", cloneEnv = "", packages = "", condaChannel = "", pythonVersion = "", condaExe = os.environ.get('CONDA_EXE')):
    """Create or Clone Conda Environments

    This is low-level internal function used by more specific creation 
    functions. It contains the main process of functionalizing the conda 
    subprocesses to create and clone Conda environments. 

    Parameters
    ----------
    newEnvLocation : str
        The path (Conda prefix) you want to use for the new environment you
        are creating.
    envYML : str
        The path to an environment.yml file you are using to create a new
        environment with. Cannot be used in combination with the 'cloneEnv'
        argument.
    cloneEnv : str
        The name or the path to an existing Conda environment you would like to 
        clone. Cannot be used in combination with the 'envYML' argument.
    packages : str or list
        What packages should be installed in the new envrionment? 
        Can be either a string or a list of strings. The default is blank and 
        will install the default version of Python unless specified with the 
        'pythonVersion' argument. Ignored if envYML or cloneEnv arguments are
        used.
    condaChannel : str
        You can specify what conda channel you what to install dependencies to
        here. Example 'conda-forge'. Default is an empty string and will ignore
        the channel argument when calling conda install. Ignored if envYML or 
        cloneEnv arguments are used.
    pythonVersion : str
        The Python version you want to install. The default value 
        will install the default version of Python. Ignored if envYML or 
        cloneEnv arguments are used.
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'

    Returns
    -------
    subprocess.CompletedProcess
        This function returns the object created by the subprocess.run function
        for creating the environment.

    """

    # Check that condaExe exists
    _checkCondaExe(condaExe)

    #Error if envYML and cloneEnv are specified
    if envYML != "" and cloneEnv != "":
        raise RuntimeError("Both 'envYML' and 'cloneEnv' were given. Only specify one.")

    #Create initial argument list (slightly different command when creating from yml file)
    # if envYML == "" and cloneEnv == "":
    if envYML == "":
        createEnvArgs = [condaExe, 'create', '--prefix', newEnvLocation, '-y']
    else:
        createEnvArgs = [condaExe, 'env', 'create', '--prefix', newEnvLocation]

    #Create from environment.yml file
    if envYML != "":
        createEnvArgs.extend(['--file', envYML])

    #Clone existing environment
    if cloneEnv != "":
        #Check environment exists
        cloneEnv = _env_resolve(condaExe, cloneEnv)

        createEnvArgs.extend(['--clone', cloneEnv])

    #Create from scratch (no YML or clone env)
    if envYML == "" and cloneEnv == "":
        
        #Add channel argument
        if condaChannel != "":
            createEnvArgs.extend(['--channel', condaChannel])

        #Add package arguments 
        if packages == "":
            #List default packages besides python (could add things like numpy or pandas in the future)
            packages = []
            if pythonVersion == "":
                packages.extend(["python"])
            else:
                packages.extend(['python=' + pythonVersion])
        else:
            #Check packages input and make sure its a list
            if isinstance(packages, str):
                packages = [packages]
            if isinstance(packages, list) == False:
                raise RuntimeError("Input for packages must be either a single string or a list of strings.")

        createEnvArgs.extend(packages)

        

    #Create environment
    print("Calling `" + " ".join(createEnvArgs) + "` in the cmd console.")
    out = subprocess.run(createEnvArgs)

    return out



def env_create(newEnvLocation, packages = "", condaChannel = "", pythonVersion = "", condaExe = os.environ.get('CONDA_EXE')):
    """Create Conda Environment from Scratch

    This is high-level function used to create Conda environments without a
    template. 

    Parameters
    ----------
    newEnvLocation : str
        The path (Conda prefix) you want to use for the new environment you
        are creating.
    packages : str or list
        What packages should be installed in the new envrionment? 
        Can be either a string or a list of strings. The default is blank and 
        will install the default version of Python unless specified with the 
        'pythonVersion' argument.
    condaChannel : str
        You can specify what conda channel you what to install dependencies to
        here. Example 'conda-forge'. Default is an empty string and will ignore
        the channel argument when calling conda install. 
    pythonVersion : str
        The Python version you want to install. The default value 
        will install the default version of Python.
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'

    Returns
    -------
    subprocess.CompletedProcess
        This function returns the object created by the subprocess.run function
        for creating the environment.

    """

    out = _env_CreateOrClone(newEnvLocation = newEnvLocation, packages = packages, condaChannel = condaChannel, pythonVersion = pythonVersion, condaExe = condaExe)

    return out



def env_create_from_YML(newEnvLocation, envYML = "", condaExe = os.environ.get('CONDA_EXE')):
    """Create Conda Environment from an environment.yml file

    This is high-level function used to create Conda environments from an
    environment.yml template file.

    Parameters
    ----------
    newEnvLocation : str
        The path (Conda prefix) you want to use for the new environment you
        are creating.
    envYML : str
        The path to an environment.yml file you are using to create a new
        environment with. 
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'

    Returns
    -------
    subprocess.CompletedProcess
        This function returns the object created by the subprocess.run function
        for creating the environment.

    """

    out = _env_CreateOrClone(newEnvLocation = newEnvLocation, envYML = envYML, condaExe = condaExe)

    return out



def env_clone(newEnvLocation, cloneEnv = "", condaExe = os.environ.get('CONDA_EXE')):
    """Clone Conda Environments use an existing environment

    This is high-level function used to create Conda environments using an 
    existing cond environment as a template.

    Parameters
    ----------
    newEnvLocation : str
        The path (Conda prefix) you want to use for the new environment you
        are creating.
    cloneEnv : str
        The name or the path to an existing Conda environment you would like to 
        clone.
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'

    Returns
    -------
    subprocess.CompletedProcess
        This function returns the object created by the subprocess.run function
        for creating the environment.

    """

    out = _env_CreateOrClone(newEnvLocation = newEnvLocation, cloneEnv = cloneEnv, condaExe = condaExe)

    return out


def env_remove(condaEnvToRemove, condaExe = os.environ.get('CONDA_EXE')):
    """Remove/Delete Conda Environment

    Removes the specified Conda environment. 

    Parameters
    ----------
    condaEnvToRemove : str
        The name or the path to an existing Conda environment you would like to 
        remove.
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'

    Returns
    -------
    subprocess.CompletedProcess
        This function returns the object created by the subprocess.run function
        for creating the environment.

    """

    # Check that condaExe exists
    _checkCondaExe(condaExe)

    #Check environment exists
    condaEnvToRemove = _env_resolve(condaExe, condaEnvToRemove)
   

    #Create argument list 
    removeEnvArgs = [condaExe, 'env', 'remove', '--prefix', condaEnvToRemove]
   
    #Create environment
    print("Calling `" + " ".join(removeEnvArgs) + "` in the cmd console.")
    out = subprocess.run(removeEnvArgs)

    return out

env_create(newEnvLocation = "L:\\CondaEnvs\\test3", packages = "", condaChannel = "", pythonVersion = "3.7")
env_create_from_YML(newEnvLocation = "L:\\CondaEnvs\\test5", envYML = "L:\\GitHub\\marcpy\\environment.yml")
env_clone(newEnvLocation = "L:\\CondaEnvs\\test6", cloneEnv = "marcRwebscraper")

env_remove(condaEnvToRemove="L:\\CondaEnvs\\test3")
env_remove(condaEnvToRemove="L:\\CondaEnvs\\test4")
env_remove(condaEnvToRemove="L:\\CondaEnvs\\test5")


pythonVersion="3.7"
packages = ["numpy", "test", "python=3.2", "test2"]
packages = ["numpy", "test", "python", "test2"]
packages = ["numpy", "test", "py", "test2"]

not any(list(map(lambda x:  x == "python" or x.startswith("python="), packages)))

env_create(newEnvLocation = "L:\\CondaEnvs\\test1", packages = "keyring", condaChannel = "", pythonVersion = "3.7")
env_create(newEnvLocation = "L:\\CondaEnvs\\test2", packages = ["keyring", 'python=3.6'], condaChannel = "", pythonVersion = "3.7")
env_create(newEnvLocation = "L:\\CondaEnvs\\test4", packages = ["numpy", 'python=3.6'], condaChannel = "", pythonVersion = "3.7")

