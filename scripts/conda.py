import os
import sys
import subprocess
import numpy
import json
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

    Python friendly output from ``conda list --prefix /path/to/env --json``.
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

    # Retrieve outpu as JSON
    rawJson = subprocess.check_output([condaExe, 'list', '--prefix', condaEnv, '--json']).decode("utf-8")
    pdJson = pandas.read_json(rawJson)

    return pdJson

