import os
import platform

try:
    import arcpy
except ImportError as e:
    eMessage = ["No module named 'arcpy'. Please install it from the 'esri' channel from Conda."]
    if platform.python_version_tuple()[0] + "." + platform.python_version_tuple()[1] != "3.7":
        eMessage.extend(["In my limited experience it may be best to rebuild your Conda envrionment with 'python=3.7' to use 'arcpy'.",
        "I have noticed that there can be issues with the installation process when using other python versions."])
    eMessage.extend(["You can use: `marcpy.conda.install_packages('arcpy', condaChannel = 'esri')` directly from python or",
    "'conda install arcpy -c esri` from your activated conda environment at the command line."])
    raise RuntimeError(("\n").join(eMessage)) from e

import pandas


def Walk(workspace, datatype = None, type = None, pathType = 'Full'):
    """List a features of a datatype or multiple datatypes.

    This is a wrapper around `arcpy.da.Walk()` that allows you to specify the 
    return path type.

    Parameters
    ----------
    workspace : str
        A folder path or gdb that you want to get a list of features from
    datatype : str
        The data type to limit the results returned. Passed directly to 
        `arcpy.da.Walk()`. See the possible values on their help here: 
        https://pro.arcgis.com/en/pro-app/latest/arcpy/data-access/walk.htm.
        It is possible to search for multiple by passing a list. Default will
        return all datatypes.
    type : str
        Feature and raster data types can be further limited by type. Passed 
        directly to `arcpy.da.Walk()`. See the possible values on their help 
        here: https://pro.arcgis.com/en/pro-app/latest/arcpy/data-access/walk.htm.
        It is possible to search for multiple by passing a list. Default will
        return all types. 
    pathType : str
        What type of filepath do you want to return. Accepts values of ['Full', 
        'Relative', 'Name']. Defaults to 'Full'.

    Returns
    -------
    list
        A list of all the features found that match the datatype arguments.
    """

    out = []

    for dirpath, dirnames, filenames in arcpy.da.Walk(workspace, datatype = datatype, type = type):

        for filename in filenames:
            if pathType == "Full":
                out.extend([os.path.join(dirpath, filename)])
            elif pathType == "Relative":
                relativePath = dirpath.replace(workspace, "")
                if relativePath.startswith("\\"):
                    relativePath = relativePath.replace("\\", "", 1)
                out.extend([os.path.join(relativePath, filename)])
            elif pathType == "Name":
                out.extend([filename])
            else:
                raise RuntimeError("'pathType' must be one of ['Full', 'Relative', 'Name']")
    
    return out

# Walk(workspace = "C:\\Users\\jpeterson\\Documents\\ArcGIS\\Projects\\MyProject1", datatype = "FeatureClass", pathType = 'Relative')
# Walk(workspace = "C:\\Users\\jpeterson\\Documents\\ArcGIS\\Projects\\MyProject1", datatype = "Table", pathType = 'Relative')
# Walk(workspace = "C:\\Users\\jpeterson\\Documents\\ArcGIS\\Projects\\MyProject1", datatype = ["FeatureClass", "RasterDataset"], pathType = 'Relative')


def WalkGDB(searchFolder = 'U:\\Projects\\GIS_Services', datatypes = ["FeatureClass", "Table", "RasterCatalog", "RasterDataset"], pathType = "Relative"):
    """Walk all Geodatabases in the search folder and get a dataframe of the features
    
    This is a wrapper around `marcpy.arcpy_wrappers.Walk()` that allows you 
    walk all geodatabes in a search path and create a pandas dataframe of  all 
    the features of particular esri datatypes found.
    
    Parameters
    ----------
    searchFolder : str
        A folder path that you want to search for features from.
    datatypes : str
        The data type to limit the results returned. Passed directly to 
        `arcpy.da.Walk()`. See the possible values on their help here: 
        https://pro.arcgis.com/en/pro-app/latest/arcpy/data-access/walk.htm.
        It is possible to search for multiple by passing a list similar to the 
        default.
    pathType : str
        What type of filepath do you want to return. Accepts values of ['Full', 
        'Relative', 'Name']. Defaults to 'Relative'.
    
    Returns
    -------
    dataframe
        A pandas dataframe of all the features found in any geodatabase in the 
        'searchFolder' path that match the datatype arguments.
    """
    
    #Make sure searchFolder exists
    if (not os.path.exists(searchFolder)):
        raise RuntimeError("The provided 'searchFolder' does not exist on your system.")
    
    
    #Create outut object to hold list of dataframes
    out = []
    
    #Walk the filesystem at 'U:\\Projects\\GIS_Services'
    for root, dirs, files in os.walk('U:\\Projects\\GIS_Services'):
        #Walk each folder
        for folder in dirs:
            #If the folder is a geodatabase
            if folder.endswith(".gdb"):
                
                #Set Env Workspace to gdb
                folderPath = os.path.join(root, folder)
                print(folderPath)
                
                #Get Features dataframe by looping over the datatypes list for each GDB
                outLst = []
                for datatype in datatypes:
                    tmp = Walk(workspace = folderPath, datatype = datatype, pathType = pathType)
                    tmp = pandas.DataFrame.from_dict({"GeoDatabase": [folderPath] * len(tmp), "Feature": tmp, "DataType": [datatype] * len(tmp)})
                    outLst.extend([tmp])
                out.extend([pandas.concat(outLst, ignore_index=True)])
                
    #Combine list of datafames into one output dataframe
    output = pandas.concat(out, ignore_index=True)
    return output


# WalkGDB()

