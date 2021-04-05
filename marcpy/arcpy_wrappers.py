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

def Walk(workspace, datatype = None, type = None, pathType = 'Full'):
    """List a features of a datatype or multiple datatypes.

    This is a wrapper around `arcpy.da.Walk()` that allows you to specify the 
    return path type.

    Parameters
    ----------
    wokspace : str
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