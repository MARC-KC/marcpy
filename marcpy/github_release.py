
import os
import platform
import pathlib
import requests
import sys
import re
import shutil
import warnings

import pandas as pd
import numpy as np
import keyring

import marcpy.jsonpath_pd
from marcpy.jsonpath_pd import JSONtoLongDataFrame


def github_get_PAT():
    PAT = None
    
    if platform.system() != "Windows":
        return(PAT)
        
    #Try username = PersonalAccessToken
    PAT = keyring.get_password(service_name="git:https://github.com", username = "PersonalAccessToken")
    
    #Try username from ~/.gitconfig
    if PAT is None:
        def _useGitUsername():
            PAT=None
            gitConfigPath = os.path.join(os.environ.get('USERPROFILE'), ".gitconfig") 
            if os.path.exists(gitConfigPath):
                with open(gitConfigPath, "r") as fp:
                    username = [re.sub("\s+", "", re.sub("^\s+name = ", "", line)) for line in fp if re.match("\s+name = ", line)]
                username = username[0] if len(username) > 0 else ''
                PAT = keyring.get_password(service_name="git:https://github.com", username = username)
            return(PAT)
        PAT = _useGitUsername()
    
    #Add warning if not found. 
    if PAT is None:
        message = """
        No PAT was found in Windows Credential Manager.
        Checked for the following keys: 
            service = "git:https://github.com"      username = "PersonalAccessToken"
            service = "git:https://github.com"      username = "<user.name entry in ~.gitconfig>"
        Please make sure you have a GIT PAT saved in Windows Credential Manager. 
        If you do and its under a different service/username than above you will need to edit `marcpy.github_release.github_get_PAT()`
        """
        warnings.warn(message)
    
    return(PAT)



def _github_release_check_install_path(path = None, subDirectory = ''):
    """Check install path exists
    
    If OS is Windows uses LOCALAPPDATA as a default path.
    
    Parameters
    ----------
    path : str
        Install path. Default None will translate to your LOCALAPPDATA env 
        variable.
    subDirectory : str
        Sub-directories to be appended to path. Left seperately from path as an 
        argument so that the default could be used and adapted to different OS's.
    
    Return
    ------
    str
        A string with verified install path.
    """
    
    if path is None:
        if platform.system() == "Windows":
            if "LOCALAPPDATA" not in os.environ:
                raise RuntimeError("Expected envrionmental variable 'LOCALAPPDATA' not found. Specify the path directly instead.")
            path = pathlib.Path(os.environ['LOCALAPPDATA'], subDirectory)
        else:
            raise RuntimeError("This is currently only setup to run on Windows OS.")
    else:
        path = pathlib.Path(path,subDirectory)
    #Ensure path exists
    if not os.path.exists(path):
        os.makedirs(path)
    return(path)


def github_release_download_file(url, file_name):
    """Download github asset
    
    Will use the PersonalAccessToken stored under the service 
    'git:https://github.com' in Windows Credential Manager if using Windows.
    
    Parameters
    ----------
    url : str
        Url for the github asset
    file_name : str
        Path with filename for the download location
    
    Return
    ------
    None
    """
    
    PAT = github_get_PAT()
    
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        if PAT is not None:
            head = {'Accept': 'application/octet-stream', 'Authorization': 'token {}'.format(PAT)}
            response = requests.get(url, headers=head)
        else:
            head = {'Accept': 'application/octet-stream'}
            response = requests.get(url, headers=head)
        # write to file
        file.write(response.content)

def github_release_download_unzip_file(path, url):
    """Download github asset and unzip the archive
    
    Will use the PersonalAccessToken stored under the service 
    'git:https://github.com' in Windows Credential Manager if using Windows.
    
    Parameters
    ----------
    url : str
        Url for the github asset
    file_name : str
        Path with filename for the download location
    
    Return
    ------
    None
    """
    
    #Download files
    # file_path =  pathlib.Path(path, url.split("/")[-1])
    github_release_download_file(url = url, file_name = path) 
    
    #Extract files
    shutil.unpack_archive(path, os.path.dirname(path))
    os.remove(path)


def github_release_json(owner, repo, per_page = 7, page = 1):
    """Download release json for a GitHub repository
    
    Will use the PersonalAccessToken stored under the service 
    'git:https://github.com' in Windows Credential Manager if using Windows.
    
    Parameters
    ----------
    owner : str
        Owner of the repository / GitHub account
    repo : str
        GitHub Repository
    per_page : int
        How many of the most recent releases should be returned? Default is 3.
    page : int
        Which page of the paginated releases should be returned? Default is the
        first page.
    
    Return
    ------
    dict 
        Dictionary representation of the downloaded JSON.
    """
    
    url = "https://api.github.com/repos/{owner}/{repo}/releases?per_page={per_page}&page={page}".format(owner=owner, repo=repo, per_page=per_page, page=page)
    
    PAT = github_get_PAT()
    
    if PAT is not None:
        head = {'Authorization': 'token {}'.format(PAT)}
        jsonRelease = requests.get(url, headers=head).json()
    else:
        jsonRelease = requests.get(url).json()
    return(jsonRelease)

def github_release_jsonDF(owner, repo, per_page = 7, page = 1):
    """Download release json for a GitHub repository and convert to DataFrame
    
    Will use the PersonalAccessToken stored under the service 
    'git:https://github.com' in Windows Credential Manager if using Windows.
    Uses jsonpath_pd.JSONtoLongDataFrame() to do the conversion.
    
    Parameters
    ----------
    owner : str
        Owner of the repository / GitHub account
    repo : str
        GitHub Repository
    per_page : int
        How many of the most recent releases should be returned? Default is 3.
    page : int
        Which page of the paginated releases should be returned? Default is the
        first page.
    
    Return
    ------
    pandas dataframe 
        Dataframe representation of the downloaded JSON.
    """
    
    jsonRelease = github_release_json(owner=owner, repo=repo, per_page=per_page, page=page)
    dfRelease = JSONtoLongDataFrame(jsonRelease)
    return(dfRelease)


def github_release_versions(owner, repo, tagVersionRegex='', tagPrefixRegex = '', tagSuffixRegex = '', per_page = 7, page=1):
    """Get release versions for a GitHub repository
    
    Will use the PersonalAccessToken stored under the service 
    'git:https://github.com' in Windows Credential Manager if using Windows.
    
    Parameters
    ----------
    owner : str
        Owner of the repository / GitHub account
    repo : str
        GitHub Repository
    tagVersionRegex : str
        The regrex to pull the version from the git tag. Often a variation of '\d+\\.\d+\\.\d+'
    tagPrefixRegex : str
        The regrex to ignore any version prefix from the git tag. May be a 'v'.
    tagSuffixRefex : str
        The regrex to ignore any version suffix from the git tag.
    per_page : int
        How many of the most recent releases should be returned? Default is 3.
    page : int
        Which page of the paginated releases should be returned? Default is the
        first page.
    
    Return
    ------
    dict
        Dictionary containing the release versions and associated tag names. 
    """
    
    dfRelease = github_release_jsonDF(owner = owner, repo = repo, per_page = per_page, page = page)
    tag_names = list(dfRelease[dfRelease['FullPath_Generalized'].str.match('\[\*\]\["tag_name"\]') & dfRelease['Value'].str.match("{tagPrefix}{tagVersion}{tagSuffix}".format(tagPrefix=tagPrefixRegex, tagVersion=tagVersionRegex, tagSuffix=tagSuffixRegex))]['Value'].values)
    release_versions = [re.sub("^{tagPrefix}|{tagSuffix}$".format(tagPrefix=tagPrefixRegex, tagSuffix=tagSuffixRegex), '', tag_name) for tag_name in tag_names]
    return({"release_versions":release_versions, "tag_names":tag_names})


# owner='MARC-KC'
# repo='MARC_META-marcpymeta'
# version = None
# assetVersion = '.tar.bz2'
# tagVersionRegex='\d+\\.\d+\\.\d+|\d+\\.\d+\\.\d+\\.\d+'
# tagPrefixRegex = 'v'
# tagSuffixRegex = ''
# assetTypeRegex = '{VERSION}-py\d+_\d+(.*)$'
# per_page = 7
# page=1
def github_release_info(owner, repo, version = None, assetVersion = None, assetTypeRegex = '(.*)', tagVersionRegex='', tagPrefixRegex = '', tagSuffixRegex = '', per_page = 7, page=1):
    """Get release info for a GitHub repository
    
    Will use the PersonalAccessToken stored under the service 
    'git:https://github.com' in Windows Credential Manager if using Windows.
    
    Parameters
    ----------
    owner : str
        Owner of the repository / GitHub account
    repo : str
        GitHub Repository
    version : str
        Optionally specify the version you want to get the information for. It 
        must be listed as a release_version in the output from 
        `github_release_versions()`. You may need to adjust per_page or page 
        arguments to get older versions. Default None will select the latest
        release.
    assetVersion : str
        The file extension or chunk of the file name of the asset from the 
        release you want to grab. This is defined by the '(.*)' section of the 
        assetTypeRegex defined below. Default None will result in an error. This 
        must be defined.
    assetTypeRegex : str
        A special regex string that defines the pattern of the release asset 
        filename. The '(.*)' section must be included and is used to match the
        assetVersion. Two other optional search parameters you can use are
        '{VERSION}' and '{VERSION_TAG}'. They will get replaced by the version 
        or the version tag identified through selections in this function. 
        Examples are '{VERSION}-py\d+_\d+(.*)$' for the marcpymeta conda package
        and '{VERSION_TAG}-(.*)$' for the geckodriver release.
    tagVersionRegex : str
        The regrex to pull the version from the git tag. Often a variation of '\d+\\.\d+\\.\d+'
    tagPrefixRegex : str
        The regrex to ignore any version prefix from the git tag. May be a 'v'.
    tagSuffixRefex : str
        The regrex to ignore any version suffix from the git tag.
    per_page : int
        How many of the most recent releases should be returned? Default is 3.
    page : int
        Which page of the paginated releases should be returned? Default is the
        first page.
    
    Return
    ------
    dict
        Dictionary containing the release versions and associated tag names. 
    """
    
    #Get versions
    latestVersions = github_release_versions(owner=owner, repo=repo, tagVersionRegex=tagVersionRegex, tagPrefixRegex=tagPrefixRegex, tagSuffixRegex=tagSuffixRegex, per_page=per_page, page=page)
    if version is None:
        version = latestVersions['release_versions'][0]
        print("No version supplied so latest version is being used: '{}'".format(version))
    
    #Check requested version is available
    if version not in latestVersions['release_versions']:
        raise  RuntimeError("Supplied version ('{version}') not found. You may need to increase the per_page or page arguments if you are searching for an older release.".format(version=version))
    version_tag = latestVersions['tag_names'][latestVersions['release_versions'].index(version)]
    
    
    #Get assetTypes for requested version
    dfRelease = github_release_jsonDF(owner = owner, repo = repo, per_page = per_page, page = page)
    potentialAssests = dfRelease[(dfRelease['FullPath_Generalized'] == '[*]["assets"][*]["name"]') & (dfRelease['Value'].str.contains(re.escape(version)))]
    potentialAssetTypeRegex = re.sub("\{VERSION\}", re.escape(version), re.sub("\{VERSION_TAG\}", re.escape(version_tag), assetTypeRegex))
    potentialAssetTypes = np.squeeze(potentialAssests['Value'].str.extract(potentialAssetTypeRegex).values).tolist()
    if isinstance(potentialAssetTypes, str):
        potentialAssetTypes = [potentialAssetTypes]
    
    #Check that assetVersion is available
    if assetVersion is None or assetVersion not in potentialAssetTypes:
        raise RuntimeError("assetVersion must be one of: {}".format(potentialAssetTypes))
    
    assetBasePath =  re.sub('\["name"\]', "", potentialAssests[potentialAssests['Value'].str.contains(re.sub('\\(\\.\\*\\)', re.escape(assetVersion), potentialAssetTypeRegex))]['FullPath'].values[0])
    # dfRelease[dfRelease['FullPath'].str.match(re.escape('[0]["assets"][0]'))]
    assetName = dfRelease[dfRelease['FullPath'] == assetBasePath + '["name"]']['Value'].values[0]
    assetBrowserDownloadUrl = dfRelease[dfRelease['FullPath'] == assetBasePath + '["browser_download_url"]']['Value'].values[0]
    assetID = dfRelease[dfRelease['FullPath'] == assetBasePath + '["id"]']['Value'].values[0]
    assetAPIUrl = dfRelease[dfRelease['FullPath'] == assetBasePath + '["url"]']['Value'].values[0]
    
    return({'assetName':assetName, 'assetID':assetID, 'assetAPIUrl':assetAPIUrl, 'assetBrowserDownloadUrl':assetBrowserDownloadUrl, 'version':version, 'version_tag':version_tag})


def check_geckodriver(path = None, version = None, assetVersion = 'win64.zip', per_page = 7, page = 1):
    """Check that geckodriver is installed in expected location
    
    Checks for specified version (or latest version if `version = None`) is 
    installed to the specified path (LOCALAPPDATA if `path = None`). If it is
    not installed it will download the specified release asset and install it.
    
    Parameters
    ----------
    path : str
        Install path. Default None will translate to your LOCALAPPDATA env 
        variable.
    version : str
        Optionally specify the version you want to install. It 
        must be listed as a release_version in the output from 
        `github_release_versions()`. You may need to adjust per_page or page 
        arguments to get older versions. Default None will select the latest
        release.
    assetVersion : str
        The chunk of the file name of the asset from the 
        release you want to grab. Defaults to 'win64.zip' as this is what we 
        use at MARC.
    per_page : int
        How many of the most recent releases should be returned? Default is 3.
    page : int
        Which page of the paginated releases should be returned? Default is the
        first page.
    
    Return
    ------
    str
        The filepath to the installed geckodriver executable.
    """
    
    releaseInfo = github_release_info(owner='mozilla', repo='geckodriver', version = version, assetVersion = assetVersion, tagVersionRegex='\d+\.\d+\.\d+', tagPrefixRegex = 'v', tagSuffixRegex = '', assetTypeRegex = '{VERSION_TAG}-(.*)$', per_page=per_page, page=page)
    installPath = _github_release_check_install_path(path = path, subDirectory = "geckodriver/{}".format(releaseInfo['version']))
    file_path = pathlib.Path(installPath, releaseInfo['assetBrowserDownloadUrl'].split("/")[-1])
    if 'geckodriver.exe' not in os.listdir(installPath):
        github_release_download_unzip_file(path = file_path, url = releaseInfo['assetAPIUrl'])
    return(str(pathlib.Path(installPath, 'geckodriver.exe')))


def check_marcpymeta(path = None, version = None, per_page = 7, page = 1):
    """Check that marcpymeta is installed in expected location
    
    Checks for specified version (or latest version if `version = None`) is 
    installed to the specified path (LOCALAPPDATA if `path = None`). If it is
    not installed it will download the specified release asset and install it.
    
    Parameters
    ----------
    path : str
        Install path. Default None will translate to your LOCALAPPDATA env 
        variable.
    version : str
        Optionally specify the version you want to install. It 
        must be listed as a release_version in the output from 
        `github_release_versions()`. You may need to adjust per_page or page 
        arguments to get older versions. Default None will select the latest
        release.
    assetVersion : str
        The chunk of the file name of the asset from the 
        release you want to grab. Defaults to '.tar.bz2' as this is the conda
        package extension.
    per_page : int
        How many of the most recent releases should be returned? Default is 3.
    page : int
        Which page of the paginated releases should be returned? Default is the
        first page.
    
    Return
    ------
    str
        The filepath to the installed marcpymeta conda package.
    """
    
    releaseInfo = github_release_info(owner='MARC-KC', repo='MARC_META-marcpymeta', version = version, assetVersion = '.tar.bz2', tagVersionRegex='\d+\\.\d+\\.\d+|\d+\\.\d+\\.\d+\\.\d+', tagPrefixRegex = 'v', tagSuffixRegex = '', assetTypeRegex = '{VERSION}-py\d+_\d+(.*)$', per_page=per_page, page=page)
    installPath = _github_release_check_install_path(path = path, subDirectory = "conda_packages/marcpymeta")
    if releaseInfo['assetName'] not in os.listdir(installPath):
        github_release_download_file(url = releaseInfo['assetAPIUrl'], file_name = pathlib.Path(installPath).joinpath(releaseInfo['assetName']) )
    return(str(pathlib.Path(installPath, releaseInfo['assetName'])))


def main(argv=None):
    check_geckodriver(path = "X:/WorkEfforts/ResearchServices/DataManagement/Metadata_AGOtoMARCMETA", version = None)
    check_geckodriver(path = None, version = None)
    check_marcpymeta(path = None, version = None)

    github_release_info(owner='mozilla', repo='geckodriver', version = None, assetVersion = 'win64.zip', tagVersionRegex='\d+\.\d+\.\d+', tagPrefixRegex = 'v', tagSuffixRegex = '', assetTypeRegex = '{VERSION_TAG}-(.*)$', per_page = 7, page=1)
    github_release_info(owner='MARC-KC', repo='MARC_META-marcpymeta', version = None, assetVersion = '.tar.bz2', tagVersionRegex='\d+\\.\d+\\.\d+|\d+\\.\d+\\.\d+\\.\d+', tagPrefixRegex = 'v', tagSuffixRegex = '', assetTypeRegex = '{VERSION}-py\d+_\d+(.*)$', per_page = 7, page=1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
