import json
import os
from io import StringIO
import sys
import subprocess
import warnings

import numpy
import pandas

condaExe = os.environ.get('CONDA_EXE')
condaEnv = os.environ.get('CONDA_PREFIX')
condaChannel = ""
packages = ['selenium', 'selenium-wire']
packages = 'git+https://github.com/MARC-KC/marcpy'

def _install_PipWithCondaDependencies(packages, condaChannel = "", condaExe = os.environ.get('CONDA_EXE'), condaEnv = os.environ.get('CONDA_PREFIX')):

    # Check that condaExe exists
    _checkCondaExe(condaExe)

    # Check if condaEnv is a path or a virtual envrionment name
    condaEnv = _env_resolve(condaExe, condaEnv)

    #Get Environment Python Executable
    condaEnvPython = os.path.join(condaEnv, "python.exe")

    #Check package input and make sure its a list
    if isinstance(packages, str):
        packages = [packages]
    if isinstance(packages, list) == False:
        raise RuntimeError("Input for packages must be either a single string or a list of strings.")

    # pkg = 'selenium'
    for pkg in packages:

        # Get an array of uninstalled package dependencies given an installation.
        depCheck = subprocess.run([condaEnvPython, '-m', 'pip', 'download', pkg, "-d", os.environ.get("TEMP")], capture_output=True)
        if depCheck.returncode != 0:
            print("Error finding package distribution in pip for the package '" + pkg + "'. Please check the name is correct.")
            # return None

        depCheck = depCheck.stdout.decode("utf-8").split("\r\n")
        depCheck = numpy.array(depCheck)[numpy.where(numpy.array(list(map(lambda x: x.startswith("Collecting "), depCheck))))[0]]
        depCheck = numpy.char.replace(depCheck, "Collecting ", "")
        depCheck = depCheck[numpy.where(depCheck != pkg)[0]]

        # depPkg = depCheck.item(0)
        for depPkg in depCheck:

            #Attempt to install from conda and pip otherwise
            try:
                # Create list of the install command arguments
                installArgs = [condaExe, 'install', depPkg]
                
                if condaChannel != "":
                    installArgs.extend(['--channel', condaChannel])

                installArgs.extend(['--prefix', condaEnv, '-y'])
                
                # Attempt to install with conda
                condaReturn = subprocess.run(installArgs)
                if condaReturn.returncode != 0:
                    print("Error installing " + depPkg + " from conda. Installing from pip instead.")
                    raise RuntimeError("")

            except:
                print('here')   
                # Install dependency from pip
                subprocess.run([condaEnvPython, '-m', 'pip', 'install', depPkg])

        out = subprocess.run([condaEnvPython, '-m', 'pip', 'install', pkg])

    return None


_install_PipWithCondaDependencies(packages = "matplotlib", condaChannel = "conda-forge")





def _install_PipWithOutCondaDependencies(packages, condaEnv = os.environ.get('CONDA_PREFIX')):

    # Check if condaEnv is a path or a virtual envrionment name
    condaEnv = _env_resolve(condaExe, condaEnv)

    #Get Environment Python Executable
    condaEnvPython = os.path.join(condaEnv, "python.exe")

    #Check packages input and make sure its a list
    if isinstance(packages, str):
        packages = [packages]
    if isinstance(packages, list) == False:
        raise RuntimeError("Input for packages must be either a single string or a list of strings.")

    #Install from pip
    argList = [condaEnvPython, '-m', 'pip', 'install']
    argList.extend(packages)
    out = subprocess.run(argList)
    if out.returncode != 0:
        raise RuntimeError("Error installing package(s) with pip. See console output from pip.")

    return None


def install_pip(packages, UseCondaDependencies = True, condaChannel = "", condaExe = os.environ.get('CONDA_EXE'), condaEnv = os.environ.get('CONDA_PREFIX')):

    if UseCondaDependencies == True:
        _install_PipWithCondaDependencies(packages = packages, condaChannel = condaChannel, condaExe = condaExe, condaEnv = condaEnv)
    elif UseCondaDependencies == False:
        _install_PipWithOutCondaDependencies(packages = packages, condaEnv = condaEnv)

    return None

def install_conda(packages, condaChannel = "", condaExe = os.environ.get('CONDA_EXE'), condaEnv = os.environ.get('CONDA_PREFIX')):

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


packages = 'selenium'
packages = ['selenium', 'selenium-wire']
UsePip = False
UsePip = [False, True]
def install_packages(packages, UsePip = False, UseCondaDependencies = True, condaChannel = "", condaExe = os.environ.get('CONDA_EXE'), condaEnv = os.environ.get('CONDA_PREFIX')):
    """A high level function to install Canda and/or Pip package(s)

    This function is mainly a wrapper around the install_Conda and install_Pip
    functions and allows one to install a list of packages from either Conda or 
    Pip, optionally attempt to install Conda based dependencies when installing 
    from Pip and optionally install from a specific Conda channel when 
    installing from Conda. It installs to the envirionment specified in condaEnv.

    If UseCondaDependencies is True, it calls a specialized installation 
    function that prioritizes dependencies to be installed from Conda instead 
    of Pip to align with best practices. This can be 
    especially useful when trying to install a package from GitHub that requires
    it to be installed by Pip, but will allow dependencies that need compiled 
    binaries to be installed from Conda without a lot of extra work.
    If UsePip is True and UseCondaDependencies is False the arguments 
    condaChannel and CondaExe are ignored.

    Parameters
    ----------
    packages : str or list of str
        What packages should be installed? Can be either a string or a list of
        strings.
    UsePip : bool or list of bool
        Should the packages be installed with Pip or Conda. The default (False)
        installs packages to Conda. Can either be a single True/False or a list 
        of True/False that is the same length of the packages argument. This 
        allows you to install some packages with Conda and some packages with 
        Pip in a single statement.
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


    #Enforce list types for packages and UsePip
    if isinstance(packages, str):
        packages = [packages]
    if isinstance(UsePip, bool):
        UsePip = [UsePip]
    if isinstance(packages, list) == False:
        raise RuntimeError("Input for packages must be either a single string or a list of strings.")
    if isinstance(UsePip, list) == False:
        raise RuntimeError("Input for UsePip must be either a single string or a list of strings.")
    
    #Check that lengths of packages and UsePip are compatable
    if len(packages) != len(UsePip):
        if len(packages) > len(UsePip) and len(UsePip) == 1:
            UsePip = UsePip * len(packages)
        else:
            raise RuntimeError("Input for UsePip should have a length of 1 or be the same length as packages")

    # packages
    # UsePip

    #Seperate into Conda and Pip package
    packagesPip = numpy.array(packages)[UsePip].tolist()
    packagesConda = numpy.array(packages)[numpy.invert(numpy.array(UsePip))].tolist()

    if len(packagesConda) > 0:
        # Install Conda packages
        install_conda(packages = packagesConda, condaChannel = condaChannel, condaExe = condaExe, condaEnv = condaEnv)

    if len(packagesPip) > 0:
        # Install Pip packages
        install_pip(packages = packagesPip, UseCondaDependencies = UseCondaDependencies, condaChannel = condaChannel, condaExe = condaExe, condaEnv = condaEnv)

    
    return None



packages = ['selenium', 'selenium-wire']
UsePip = False
UsePip = [False, True] 
install_packages(packages = ['selenium', 'selenium-wire'], UsePip = [False, True])