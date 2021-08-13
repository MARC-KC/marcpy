from marcpy import keyring_wrappers

try:
    import arcgis
    import arcgis.gis
except ImportError as e:
    eMessage = ["No module named 'arcgis'. Please install it from the 'esri' channel from Conda."]
    if platform.python_version_tuple()[0] + "." + platform.python_version_tuple()[1] != "3.7":
        eMessage.extend(["In my limited experience it may be best to rebuild your Conda envrionment with 'python=3.7' to use 'arcgis'.",
        "I have noticed that there can be issues with the installation process when using other python versions."])
    eMessage.extend(["You can use: `marcpy.conda.install_packages('arcgis', condaChannel = 'esri')` directly from python or",
    "'conda install arcgis -c esri` from your activated conda environment at the command line."])
    raise RuntimeError(("\n").join(eMessage)) from e


def connectArcGISOnline(username = "pro"):
    """Create connection for the {arcgis} python API using keyring
    
    Creates connection to the {arcgis} python API using the data contained 
    in keyrings (managed securely by the Windows Credential Manager). This is 
    generally used for internal purposes at MARC to make 
    these connections a lazier and safer proccess with {keyring}. See 
    documentation at ### to set up database connection keys.
    
    Parameters
    ----------
    databaseString : str 
        The username for the ArcGIS Online account you want to connect to. The default
        "pro" will attempt to connect with the account you are signed into 
        ArcGIS Pro with.
    
    Returns
    -------
    arcgis.gis.GIS
        An ArcGIS connection.
    """
    
    if username == "pro":
        conn = arcgis.gis.GIS(username)
    else:
        password = keyring_wrappers.key_get("ArcGISOnline", username)
        conn = arcgis.gis.GIS(username=username, password=password)
    
    return conn

# connectArcGISOnline()
# connectArcGISOnline(username="jpeterson_MARC_GIS")
# connectArcGISOnline(username="MARC_Admin")


