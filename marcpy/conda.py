"""This module holds helper functions for working with and managing Conda
environments.
"""
import json
import os
from io import StringIO
import sys
import subprocess
import warnings

import numpy
import pandas


def _checkCondaExe(condaExe = os.environ.get('CONDA_EXE')):
    """Checks existance of the supplied conda executable path
    
    This function produces a RuntimeError if not found. 
    This function is used internally.

    Parameters
    ----------
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'

    Returns
    -------
    None
        The function has no return value
    """

    if not os.path.exists(condaExe):
        raise RuntimeError("'condaExe' at the specified path ('" + condaExe + "') does not exist.")


def list_envs(condaExe = os.environ.get('CONDA_EXE')):
    """List all conda environments

    Python friendly output from ``conda env list --json``.
    Uses the subprocess module to run the conda command line function
    from Python.

    Parameters
    ----------
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'

    Returns
    -------
    list
        A list of conda environments
    """

    # Check that condaExe exists
    _checkCondaExe(condaExe)

    rawJson = subprocess.check_output([condaExe, 'env', 'list', '--json']).decode("utf-8")
    prefix = json.loads(rawJson)['envs']
    name = list(map(lambda x: os.path.basename(x), prefix))
    out = {"name": name, "prefix": prefix}
    return out


def _env_resolve(condaExe = os.environ.get('CONDA_EXE'), condaEnv = os.environ.get('CONDA_PREFIX')):
    """Verify and resolve specified conda environment

    Verifies that the supplied conda environment exists by comparing 
    it to the environments found in conda.list_envs. This function
    can handle being given an environment name or its prefix (full 
    file path ending with the environment name).
    This is an internal function.

    Parameters
    ----------
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'
    condaEnv : str
        A conda environment. Can either be the name of the environment
        or the full file path ending with the environment (prefix). 
        Defaults to the environmental variable 'CONDA_PREFIX'.

    Returns
    -------
    str
        The full file path to the specified environment (prefix).
    """
    # Check that condaExe exists
    _checkCondaExe(condaExe)

    #get list of conda envrionments
    env_list = list_envs(condaExe)

    #if a conda environment name was supplied
    if os.path.dirname(condaEnv) == '':
        if condaEnv not in env_list['name']:
            raise RuntimeError("Could not find the virtual environment '" + condaEnv + "'. Try specifying the full path to the environment.")
        else:
            numCondaEnv = numpy.size(numpy.where(numpy.isin(env_list['name'], condaEnv)))
            if numCondaEnv > 1:
                raise RuntimeError("There are " + str(numCondaEnv) + " virtual environments that go by the name '" + condaEnv + "'. Try specifying the full path to the environment. Look at the output of 'marcPy.conda.list_envs()' for help.")

            condaEnv = env_list['prefix'][env_list['name'].index(condaEnv)]

    #if a file path to the environment was supplied       
    else:
        if condaEnv not in env_list['prefix']:
            raise RuntimeError("Could not find the virtual environment: '" + condaEnv + "'. Check the specified path to the environment.")
    
    return condaEnv


def list_packages(condaExe = os.environ.get('CONDA_EXE'), condaEnv = os.environ.get('CONDA_PREFIX')):
    """List packages installed in the specified conda environment

    Python friendly output from a combination  of 
    `conda list --prefix /path/to/env` and `python -m pip freeze`.
    
    While I recommend using conda and their snapshots, I found that some 
    conda installations fail to identify pip installations and always fail to 
    properly manage pip installs from github. This checks both sources, does
    some comparisons to weed out duplicates and then print out a combined
    table. I would consider this a more robust method for checking 
    package installations.

    Uses the subprocess module to run the conda command line function
    from Python.

    Parameters
    ----------
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'
    condaEnv : str
        A conda environment. Can either be the name of the environment
        or the full file path ending with the environment (prefix). 
        Defaults to the environmental variable 'CONDA_PREFIX'.

    Returns
    -------
    DataFrame
        A pandas DataFrame with list of installed packages and their 
        installation information in the specifed environment.
    """

    # Check that condaExe exists
    _checkCondaExe(condaExe)

    # Check if condaEnv is a path or a virtual envrionment name
    condaEnv = _env_resolve(condaExe, condaEnv)

    #Get Environment Python Executable
    condaEnvPython = os.path.join(condaEnv, "python.exe")

    #+++++++++++++++++++++++++++++
    #Get conda packages `conda env export --prefix /path/to/conda/env`
    #+++++++++++++++++++++++++++++
    #Retrieve snapshot
    condaSnapshot = subprocess.check_output([condaExe, 'env', 'export', '--prefix', condaEnv]).decode("utf-8").split("\r\n")
    condaSnapshot = numpy.array(condaSnapshot)

    #Parse out the conda installed package rows from the output
    beg = numpy.where(numpy.char.find(condaSnapshot, 'dependencies:') != -1)[0].item(0) + 1

    if numpy.size(numpy.where(numpy.char.find(condaSnapshot, '  - pip:') != -1)) != 0:
        #has pip list
        end = numpy.where(numpy.char.find(condaSnapshot, '  - pip:') != -1)[0].item(0)
    else:
        end = numpy.where(numpy.char.find(condaSnapshot, 'prefix: ') == 0)[0].item(0)

    condaOut = condaSnapshot[beg:end]

    #Parse out the package names and versions
    condaOut = numpy.char.replace(condaOut, "  - ", "")
    condaNames = numpy.array(list(map(lambda x: x.split("=")[0], condaOut)))
    condaVersions = numpy.array(list(map(lambda x: x.split("=")[1], condaOut)))
    #+++++++++++++++++++++++++++++


    #+++++++++++++++++++++++++++++  
    #Get pip packages `python -m pip freeze`
    #+++++++++++++++++++++++++++++
    #Retrieve snapshot
    pipSnapshot = subprocess.check_output([condaEnvPython, '-m', 'pip', 'freeze']).decode("utf-8").split("\r\n")

    #Parse out package names
    pipOut = numpy.array(list(map(lambda x: x.split("=")[0], pipSnapshot[:-1])))
    pipNames = numpy.array(list(map(lambda x: x.split(" ")[0], pipOut)))
    #+++++++++++++++++++++++++++++



    #+++++++++++++++++++++++++++++  
    #Compare and get pip only packages (Step 1)
    #  I used slightly fuzzy matching becasue sometimes pip/conda switch '_' for a '-' and vice versa and forces both to lowercase
    #  Step 1 is a quick check only looking at package names exactly. Step 2 will look for simularities in name and compare versions
    #+++++++++++++++++++++++++++++
    condaNamesFuzzy = numpy.char.replace(condaNames, "_", "-")
    condaNamesFuzzy = numpy.array(list(map(lambda x: x.lower(), condaNamesFuzzy)))
    pipNamesFuzzy = numpy.char.replace(pipNames, "_", "-")
    pipNamesFuzzy = numpy.array(list(map(lambda x: x.lower(), pipNamesFuzzy)))
    numPipOnly = numpy.size(numpy.where(numpy.isin(pipNamesFuzzy, condaNamesFuzzy, invert = True)))
    #+++++++++++++++++++++++++++++


    #+++++++++++++++++++++++++++++ 
    # Get json version of packages from `conda list --prefix /paht/to/conda/env --json`
    # This function has had a bug for at least 6 years (https://github.com/conda/conda/issues/1775) where it
    #    excludes Pip packages in the json return.
    #+++++++++++++++++++++++++++++
    #Pull the JSON and format it into a python table
    rawJson = subprocess.check_output([condaExe, 'list', '--prefix', condaEnv, '--json']).decode("utf-8")
    pdJson = pandas.read_json(StringIO(rawJson))
    pdOut = pdJson[["name", "version", "channel"]]
    pdOut = pdOut.assign(pipRemote=numpy.nan)

    #If pip is not providing packages just return the formatted output fromm `conda list --prefix /paht/to/conda/env --json`
    if numPipOnly == 0:    
        return pdOut
    #+++++++++++++++++++++++++++++




    #+++++++++++++++++++++++++++++
    #If pip is supplying packages, pull the necessary information to reproduce them to 
    #  force add to the package list.
    #+++++++++++++++++++++++++++++
    #Loop through the extra pip names and parse out version and/or remote information
    #Remotes will allow more robustness and automatic handling of github packages
    pipNamesToAdd = pipNames[numpy.isin(pipNamesFuzzy, condaNamesFuzzy, invert = True)]
    pipVersionsToAdd = [''] * numpy.size(pipNamesToAdd)
    pipRemotesToAdd = [''] * numpy.size(pipNamesToAdd)
    for x in range(numpy.size(pipNamesToAdd)):
        pipInfo = subprocess.check_output([condaEnvPython, '-m', 'pip', 'show', pipNamesToAdd[x]]).decode("utf-8").split("\r\n")
        pipVersion = pipInfo[numpy.where(numpy.char.find(pipInfo, 'Version: ') != -1)[0].item(0)]
        pipVersionsToAdd[x] = numpy.char.replace(pipVersion, "Version: ", "").item(0)
        pipRemotesToAdd[x] = numpy.char.replace(pipOut[numpy.where(numpy.char.find(pipOut, pipNamesToAdd[x]) != -1)[0].item(0)], pipNamesToAdd[x] + " @ ", "").item(0)
        if pipNamesToAdd[x] == pipRemotesToAdd[x] or pipRemotesToAdd[x].startswith("file:///"):
            pipRemotesToAdd[x] = numpy.nan
    #+++++++++++++++++++++++++++++



    #+++++++++++++++++++++++++++++
    #Compare and get pip only packages (Step 2)
    #  Step 2 will look for simularities in name and compare versions 
    #  Similar conda packages will take precedence
    #+++++++++++++++++++++++++++++
    pipNamesFuzzyToAdd = pipNamesFuzzy[numpy.isin(pipNamesFuzzy, condaNamesFuzzy, invert = True)]
    pipNamesFuzzyFlag = [True] * numpy.size(pipNamesToAdd)
    for x in range(numpy.size(pipNamesFuzzyToAdd)):
        condaVersionNames = pdOut.loc[(pdOut.version == pipVersionsToAdd[x]), 'name'].values.astype('str')
        condaVersionNamesFlagID1 = numpy.where(numpy.char.find(condaVersionNames, pipNamesFuzzyToAdd[x]) != -1)
        condaVersionNamesFlagID2 = numpy.where(numpy.array(list(map(lambda i: numpy.char.find(pipNamesFuzzyToAdd[x], i).item(0), condaVersionNames))) != -1)
        condaVersionNamesFlagID = numpy.append(condaVersionNamesFlagID1[0], condaVersionNamesFlagID2[0])
        if numpy.size(condaVersionNamesFlagID) != 0:
            pipNamesFuzzyFlag[x] = False
            warnings.warn("Potential name conflict between conda and pip snapshots. '" + condaVersionNames[condaVersionNamesFlagID[0].item(0)] + "' from conda and '" + pipNamesToAdd[x] + "' from pip both have the same version: " + pipVersionsToAdd[x] + ".")
            warnings.warn("This conflict will be ignored and '" + pipNamesToAdd[x] + "' will not be considered as a pip package. If this causes an issue please edit marcpy.conda.list_packages()")
    
    #filter numpy arrays by the conflict flags
    pipNamesFuzzyFlag = numpy.array(pipNamesFuzzyFlag)
    pipNamesToAdd = pipNamesToAdd[pipNamesFuzzyFlag]
    pipVersionsToAdd = numpy.array(pipVersionsToAdd)[pipNamesFuzzyFlag]
    pipRemotesToAdd = numpy.array(pipRemotesToAdd)[pipNamesFuzzyFlag]
    #+++++++++++++++++++++++++++++


    #+++++++++++++++++++++++++++++
    #Format the return into a pandas dataframe and combine with the conda packages for output
    pdPip = pandas.DataFrame({'name':pipNamesToAdd, 'version':pipVersionsToAdd, 'channel':numpy.array(['pypi'] * numpy.size(pipNamesToAdd)), 'pipRemote':pipRemotesToAdd})
    pdPip['name'] = pdPip['name'].str.lower()
    pdCombined = pdOut.append(pdPip, ignore_index = True)
    pdCombined = pdCombined.sort_values(by = 'name', ignore_index = True)


    return pdCombined




def __createPipDependency(row, generalizeGitRemotes = False):
    """Creates Pip dependency section for Conda snapshot

    This function is used internally by the snapshot() function within a
    pandas.apply function and is for internal use in the module only.

    Parameters
    ----------
    row : panda.Series
        A row slice of a pandas data frame from the package list DataFrame
    generalizeGitRemotes : bool
        Should git remotes be generalized. In other words, should everything 
        be removed in URL after and including the @ symbol that defines the
        branch or installed commmit. Defaults to False.

    Returns
    -------
    str
        A string containing the formatted pip install line for a condas
        environment.yml for that row.
    """

    #Format the input array as a string
    row = row.astype('str')
 
    #Switch to deal with 'nan' values and git repositories. Error if other.
    if row['pipRemote'] == 'nan':
        out = '    - ' + row['name'] + '==' + row['version']
    elif row['pipRemote'].startswith("git+"):
        if generalizeGitRemotes:
            out = '    - ' + row['pipRemote'].split('@')[0]
        else:
            out = '    - ' + row['pipRemote']
        
    else:
        raise RuntimeError("The pipRemote for '" + row['name'] + "' is not recognized: '" + row['pipRemote'] + "'. Expected 'nan' or a git remote. If something else needs added edit marcpy.conda._createPipDependency().")

    return out



def env_snapshot(condaExe = os.environ.get('CONDA_EXE'), condaEnv = os.environ.get('CONDA_PREFIX'), envYMLloc = os.getcwd(), generalizeGitRemotes = False):
    """Create environment.yml snapshot for the specified conda environment

    Conda friendly snapshot from a combination  of 
    `conda list --prefix /path/to/env` and `python -m pip freeze`.
    
    While I recommend using conda and their snapshots, I found that some 
    conda installations fail to identify pip installations and always fail to 
    properly manage pip installs from github. This uses list_packages() to 
    check both sources, does some comparisons to weed out duplicates and then 
    manually create the pip install section of the environmetn.yml file. I 
    would consider this a more robust method for checking creating environment 
    snapshots.

    Parameters
    ----------
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'
    condaEnv : str
        A conda environment. Can either be the name of the environment
        or the full file path ending with the environment (prefix). 
        Defaults to the environmental variable 'CONDA_PREFIX'.
    envYMLloc : str
        The directory location you want to same the environment.yml snapshot
        file to. Defaults to the current working directory at os.getcwd().
    generalizeGitRemotes : bool
        Should git remotes be generalized. In other words, should everything 
        be removed in URL after and including the @ symbol that defines the
        branch or installed commmit. Defaults to False.

    Returns
    -------
    None
        The environment.yml file is created at the specified location and prints
        it out the the console.
    """

    # Check that condaExe exists
    _checkCondaExe(condaExe)

    # Check if condaEnv is a path or a virtual envrionment name
    condaEnv = _env_resolve(condaExe, condaEnv)

    #Check that envYMLloc exists
    if not os.path.exists(envYMLloc):
        warnings.warn("'envYMLloc' at the specified path ('" + condaExe + "') does not exist. Creating path now.")
        os.makedirs(envYMLloc, exist_ok=True)
    envYMLloc = os.path.join(envYMLloc, "environment.yml")

    # Get package list
    pdEnvList = list_packages(condaExe, condaEnv)

    # Check for pypi, if none export environment.yml
    pdPyPi = pdEnvList.loc[(pdEnvList.channel == 'pypi')]
    if pdPyPi.shape[0] == 0:
        print("Exporting to " + envYMLloc)
        with open(envYMLloc, 'w') as f:
            subprocess.run([condaExe, 'env', 'export', '--prefix', condaEnv], stdout=f)



    #+++++++++++++++++++++++++++++
    #Get conda packages `conda env export --prefix /path/to/conda/env`
    #+++++++++++++++++++++++++++++
    #Retrieve snapshot
    condaSnapshot = subprocess.check_output([condaExe, 'env', 'export', '--prefix', condaEnv, '--no-builds']).decode("utf-8").split("\r\n")
    condaSnapshot = numpy.array(condaSnapshot)
    #+++++++++++++++++++++++++++++


    #+++++++++++++++++++++++++++++ 
    #Parse out snapshot pieces, manually create pip install section, and recombine together
    #+++++++++++++++++++++++++++++
    #Parse out the conda installed package rows from the output
    if numpy.size(numpy.where(numpy.char.find(condaSnapshot, '  - pip:') != -1)) != 0:
        #has pip list
        endCondaDep = numpy.where(numpy.char.find(condaSnapshot, '  - pip:') != -1)[0].item(0)
    else:
        endCondaDep = numpy.where(numpy.char.find(condaSnapshot, 'prefix: ') == 0)[0].item(0)

    prefixCondaDep = numpy.where(numpy.char.find(condaSnapshot, 'prefix: ') == 0)[0].item(0)

    #Slice out everything before and after the pip packages (Parts 1 and 3) and create pip section manually
    condaPart1 = condaSnapshot[:endCondaDep]
    condaPart2 = numpy.append(numpy.array(['  - pip:']), pdPyPi.apply(lambda row: __createPipDependency(row, generalizeGitRemotes), axis = 1).values.astype('str'))
    condaPart3 = condaSnapshot[prefixCondaDep:]

    #Combine the data back together
    condaSnapshotOutput = numpy.append(numpy.append(condaPart1, condaPart2), condaPart3)
    condaSnapshotOutput = "\n".join(condaSnapshotOutput)
    #+++++++++++++++++++++++++++++

    #Write condaSnapshotOutput to a file
    f = open(envYMLloc, "w")
    f.write(condaSnapshotOutput)
    f.close()

    #Print the file to console
    print(condaSnapshotOutput)



def install_conda(packages, condaChannel = "", condaExe = os.environ.get('CONDA_EXE'), condaEnv = os.environ.get('CONDA_PREFIX')):
    """Install Conda package(s)

    A wrapper for the console command: 
    conda install pkg1 pkg2 ... --channel $condaChannel --prefix /pth/to/Conda/env -y
    If condaChannel is left unaltered the channel arguments will be left out.

    Parameters
    ----------
    packages : str or list
        What packages should be installed? Can be either a string or a list of
        strings.
    condaChannel : str
        You can specify what conda channel you what to install dependencies to
        here. Example 'conda-forge'. Default is an empty string and will ignore
        the channel argument when calling conda install.
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'
    condaEnv : str
        A conda environment. Can either be the name of the environment
        or the full file path ending with the environment (prefix). 
        Defaults to the environmental variable 'CONDA_PREFIX'.

    Returns
    -------
    None
        This function returns nothing.
    """

    # Check that condaExe exists
    _checkCondaExe(condaExe)

    # Check if condaEnv is a path or a virtual envrionment name
    condaEnv = _env_resolve(condaExe, condaEnv)

    #Check packages input and make sure its a list
    if isinstance(packages, str):
        packages = [packages]
    if isinstance(packages, list) == False:
        raise RuntimeError("Input for packages must be either a single string or a list of strings.")

    #Print Statement
    printHighlighter = "############################################################################"
    print(printHighlighter)
    print("Installing the following packages with Conda: '" + "', '".join(packages) + "'.")
    print(printHighlighter)

    # Create list of the install command arguments
    installArgs = [condaExe, 'install']
    installArgs.extend(packages)
    
    if condaChannel != "":
        installArgs.extend(['--channel', condaChannel])

    installArgs.extend(['--prefix', condaEnv, '-y'])
    
    # Attempt to install with conda
    condaReturn = subprocess.run(installArgs)
    if condaReturn.returncode != 0:
        raise RuntimeError("Error installing " + depPkg + " from conda. Installing from pip instead.")

    return None


def __install_pip_subprocess(packages, condaEnvPython):
    """Install packages with Pip (main subprocess call)

    This is an entirely internal function. It is called by 
    _install_PipWithOutCondaDependencies and _install_PipWithCondaDependencies
    and all it just holds the process of functionalizing the pip subprocess 
    call.

    Parameters
    ----------
    packages : str or list
        What packages should be installed? Can be either a string or a list of
        strings.
    condaEnv : str
        The python path in a conda environment. This should be resolved and 
        checked in the function that calls this function.

    Returns
    -------
    subprocess.run object
        This function returns the object created by the subprocess run function
        for installing pip packages.

    """
    #Check packages input and make sure its a list
    if isinstance(packages, str):
        packages = [packages]
    if isinstance(packages, list) == False:
        raise RuntimeError("Input for packages must be either a single string or a list of strings.")

    #Print Statement
    printHighlighter = "############################################################################"
    print(printHighlighter)
    print("Installing the following packages with Pip: '" + "', '".join(packages) + "'.")
    print(printHighlighter)

    #Install from pip
    argList = [condaEnvPython, '-m', 'pip', 'install']
    argList.extend(packages)
    out = subprocess.run(argList)

    return out


def _install_PipWithCondaDependencies(packages, condaChannel = "", condaExe = os.environ.get('CONDA_EXE'), condaEnv = os.environ.get('CONDA_PREFIX')):
    """Install Pip package(s), but prioritize dependency installation from Conda

    A specialized installation function that prioritizes dependencies to be 
    installed from Conda instead of Pip to match best practices. This can be 
    especially useful when trying to install a package from GitHub that requires
    it to be installed by Pip, but will allow dependencies that need compiled 
    binaries to be installed from Conda without a lot of extra work.

    Parameters
    ----------
    packages : str or list
        What packages should be installed? Can be either a string or a list of
        strings.
    condaChannel : str
        You can specify what conda channel you what to install dependencies to
        here. Example 'conda-forge'. Default is an empty string and will ignore
        the channel argument when calling conda install.
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'
    condaEnv : str
        A conda environment. Can either be the name of the environment
        or the full file path ending with the environment (prefix). 
        Defaults to the environmental variable 'CONDA_PREFIX'.

    Returns
    -------
    None
        This function returns nothing.
    """

    # Check that condaExe exists
    _checkCondaExe(condaExe)

    # Check if condaEnv is a path or a virtual envrionment name
    condaEnv = _env_resolve(condaExe, condaEnv)

    #Get Environment Python Executable
    condaEnvPython = os.path.join(condaEnv, "python.exe")

    #Check packages input and make sure its a list
    if isinstance(packages, str):
        packages = [packages]
    if isinstance(packages, list) == False:
        raise RuntimeError("Input for packages must be either a single string or a list of strings.")

    # pkg = 'selenium'
    for pkg in packages:

        # Get an array of uninstalled package dependencies given an installation.
        depCheck = subprocess.run([condaEnvPython, '-m', 'pip', 'download', pkg, "-d", os.environ.get("TEMP")], capture_output=True)
        if depCheck.returncode != 0:
            raise RuntimeError("Error finding package distribution in pip for the package '" + pkg + "'. Please check the name is correct.")
            

        depCheck = depCheck.stdout.decode("utf-8").split("\r\n")
        depCheck = numpy.array(depCheck)[numpy.where(numpy.array(list(map(lambda x: x.startswith("Collecting "), depCheck))))[0]]
        depCheck = numpy.char.replace(depCheck, "Collecting ", "")
        depCheck = depCheck[numpy.where(depCheck != pkg)[0]]

        # depPkg = depCheck.item(0)
        for depPkg in depCheck:

            #Attempt to install from conda and pip otherwise
            try:
                
                # Attempt to install with conda
                install_conda(packages = depPkg, condaChannel = condaChannel, condaExe = condaExe, condaEnv = condaEnv) 

            except Exception as e:
                print(e)
                # Install dependency from pip
                tmp = __install_pip_subprocess(packages = packages, condaEnvPython = condaEnvPython)


        out = __install_pip_subprocess(packages = packages, condaEnvPython = condaEnvPython)

    return None


def _install_PipWithOutCondaDependencies(packages, condaEnv = os.environ.get('CONDA_PREFIX')):
    """Install Pip package(s)

    A wrapper for the console command: 
    python -m pip install pkg1 pkg2 ... 
    It installs to the envirionment specified in condaEnv.

    Parameters
    ----------
    packages : str or list
        What packages should be installed? Can be either a string or a list of
        strings.
    condaEnv : str
        A conda environment. Can either be the name of the environment
        or the full file path ending with the environment (prefix). 
        Defaults to the environmental variable 'CONDA_PREFIX'.

    Returns
    -------
    None
        This function returns nothing.
    """

    # Check if condaEnv is a path or a virtual envrionment name
    condaEnv = _env_resolve(condaExe, condaEnv)

    #Get Environment Python Executable
    condaEnvPython = os.path.join(condaEnv, "python.exe")

    #Install with pip
    out = __install_pip_subprocess(packages = packages, condaEnvPython = condaEnvPython)
    if out.returncode != 0:
        raise RuntimeError("Error installing package(s) with pip. See console output from pip.")

    return None


def install_pip(packages, UseCondaDependencies = True, condaChannel = "", condaExe = os.environ.get('CONDA_EXE'), condaEnv = os.environ.get('CONDA_PREFIX')):
    """A high level function to install Pip package(s)

    This function is mainly a wrapper around the console command:
    python -m pip install pkg1 pkg2 ... 
    It installs to the envirionment specified in condaEnv.
    If UseCondaDependencies is True, it calls a specialized installation 
    function that prioritizes dependencies to be installed from Conda instead 
    of Pip to align with best practices. This can be 
    especially useful when trying to install a package from GitHub that requires
    it to be installed by Pip, but will allow dependencies that need compiled 
    binaries to be installed from Conda without a lot of extra work.
    If UseCondaDependencies is False the arguments condaChannel and CondaExe
    are ignored.

    Parameters
    ----------
    packages : str or list
        What packages should be installed? Can be either a string or a list of
        strings.
    UseCondaDependencies : bool
        Should dependencies be attempted to be installed with Conda instead of 
        Pip? Default is True.
    condaChannel : str
        You can specify what conda channel you what to install dependencies to
        here. Example 'conda-forge'. Default is an empty string and will ignore
        the channel argument when calling conda install.
    condaExe : str 
        A conda executable path. Defaults to the 
        environmental variable 'CONDA_EXE'
    condaEnv : str
        A conda environment. Can either be the name of the environment
        or the full file path ending with the environment (prefix). 
        Defaults to the environmental variable 'CONDA_PREFIX'.

    Returns
    -------
    None
        This function returns nothing.
    """


    if UseCondaDependencies == True:
        _install_PipWithCondaDependencies(packages = packages, condaChannel = condaChannel, condaExe = condaExe, condaEnv = condaEnv)
    elif UseCondaDependencies == False:
        _install_PipWithOutCondaDependencies(packages = packages, condaEnv = condaEnv)

    return None
