# conda install python=3.7 numpy pandas keyring pyodbc sqlalchemy
# conda install arcpy --channel esri
# pip install git+https://github.com/MARC-KC/marcpy
# pip install -e L:\GitHub\marcpy


#+++++++++++++++++++++++++++++++
# Using Canda and pip from the python REPL
#+++++++++++++++++++++++++++++++
import marcpy

marcpy.conda.list_envs()
marcpy.conda.list_packages()

marcpy.conda.env_snapshot()
marcpy.conda.env_snapshot(generalizeGitRemotes=True)

marcpy.conda.env_create(newEnvLocation = "L:\\CondaEnvs\\test3", packages = "", condaChannel = "", pythonVersion = "3.7")
marcpy.conda.env_create_from_YML(newEnvLocation = "L:\\CondaEnvs\\test4", envYML = "L:\\GitHub\\marcpy\\environment.yml")
marcpy.conda.env_clone(newEnvLocation = "L:\\CondaEnvs\\test5", cloneEnv = "marcRwebscraper")

marcpy.conda.env_remove(condaEnvToRemove="L:\\CondaEnvs\\test3")
marcpy.conda.env_remove(condaEnvToRemove="L:\\CondaEnvs\\test4")
marcpy.conda.env_remove(condaEnvToRemove="L:\\CondaEnvs\\test5")


marcpy.conda.install_packages(packages = ['selenium', 'selenium-wire'], UsePip = [False, True], UseCondaDependencies=True)
marcpy.conda.install_pip(packages = 'selenium-wire', UseCondaDependencies=True, condaChannel="conda-forge")
marcpy.conda.install_conda(packages = ['selenium'])
#+++++++++++++++++++++++++++++++

#Example for setting up a new envrionment with arcpy and marcpy
newCondaEnv = "X:\DataDevelopment\Administrative\MARCAGOtoMARCMETA\CondaEnvs\MARCAGOtoMARCMETA2"
marcpy.conda.env_create(newEnvLocation = newCondaEnv, packages = ["python=3.7", 'numpy', 'pandas', 'keyring', "pyodbc"], condaChannel = "")
marcpy.conda.install_conda(packages = ['arcpy'], condaChannel="esri", condaEnv = newCondaEnv)
marcpy.conda.install_pip(packages = ["git+https://github.com/MARC-KC/marcpy"], UseCondaDependencies = False, condaEnv = newCondaEnv)


#+++++++++++++++++++++++++++++++
# Using Keyring and the Windows Credential Manager
#+++++++++++++++++++++++++++++++
import marcpy

# marcpy.key_set(serviceName="DB_conn", userName="MARC_PRD.marcdl")
# marcpy.key_get(serviceName="DB_conn", userName="MARC_PRD.marcdl")
marcpy.key_set(serviceName="DB_conn", userName="knights.marc_prd.marcdl")
marcpy.key_get(serviceName="DB_conn", userName="knights.marc_prd.marcdl")

# marcpy.key_set(serviceName="DB_conn", userName="MARC_PUB.marcpub")
# marcpy.key_get(serviceName="DB_conn", userName="MARC_PUB.marcpub")
marcpy.key_set(serviceName="DB_conn", userName="chiefs.marc_pub.marcpub")
marcpy.key_get(serviceName="DB_conn", userName="chiefs.marc_pub.marcpub")

# marcpy.key_set(serviceName="DB_conn", userName="MARC_DEV.marcpub")
# marcpy.key_get(serviceName="DB_conn", userName="MARC_DEV.marcpub")
marcpy.key_set(serviceName="DB_conn", userName="phantoms.marc_dev.marcpub")
marcpy.key_get(serviceName="DB_conn", userName="phantoms.marc_dev.marcpub")

# marcpy.key_set(serviceName="DB_conn", userName="MARC_DEV.marcdl")
# marcpy.key_get(serviceName="DB_conn", userName="MARC_DEV.marcdl")
marcpy.key_set(serviceName="DB_conn", userName="phantoms.marc_dev.marcdl")
marcpy.key_get(serviceName="DB_conn", userName="phantoms.marc_dev.marcdl")

# marcpy.key_set(serviceName="DB_conn", userName="MARC_META.marcpub")
# marcpy.key_get(serviceName="DB_conn", userName="MARC_META.marcpub")
marcpy.key_set(serviceName="DB_conn", userName="chiefs.marc_meta.marcpub")
marcpy.key_get(serviceName="DB_conn", userName="chiefs.marc_meta.marcpub")

# marcpy.key_set(serviceName="DB_conn", userName="MARC_META_dev.marcpub")
# marcpy.key_get(serviceName="DB_conn", userName="MARC_META_dev.marcpub")
marcpy.key_set(serviceName="DB_conn", userName="phantoms.marc_meta.marcpub")
marcpy.key_get(serviceName="DB_conn", userName="phantoms.marc_meta.marcpub")

marcpy.key_set(serviceName="DB_conn", userName="chiefs.tiptracker.tiptracker")
marcpy.key_get(serviceName="DB_conn", userName="chiefs.tiptracker.tiptracker")

marcpy.key_set(serviceName="DB_conn", userName="chiefs.tr_lrtp.saapp")
marcpy.key_get(serviceName="DB_conn", userName="chiefs.tr_lrtp.saapp")


# Driver={ODBC Driver 17 for SQL Server};Server=<serverName>;Database=<databaseName>;UID=<schemaName>;PWD=<password>;

# Driver={ODBC Driver 17 for SQL Server};Server=chiefs;Database=MARC_PUB;UID=marcpub;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=knights;Database=MARC_PRD;UID=marcdl;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=phantoms;Database=MARC_DEV;UID=marcpub;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=phantoms;Database=MARC_DEV;UID=marcdl;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=chiefs;Database=MARC_META;UID=marcpub;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=phantoms;Database=MARC_META;UID=marcpub;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=chiefs;Database=tiptracker;UID=tiptracker;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=chiefs;Database=tr_lrtp;UID=saapp;PWD=<password>;


#Passwords for the username should be stored in Keeper
marcpy.key_set(serviceName="ArcGIS", userName="jpeterson_MARC_GIS")
marcpy.key_get(serviceName="ArcGIS", userName="jpeterson_MARC_GIS")
marcpy.key_set(serviceName="ArcGIS", userName="MARC_Admin")
marcpy.key_get(serviceName="ArcGIS", userName="MARC_Admin")



marcpy.key_set(serviceName="", userName="API_KEY")
marcpy.key_get(serviceName="", userName="API_KEY")
marcpy.key_delete(serviceName="", userName="API_KEY")


#+++++++++++++++++++++++++++++++



#+++++++++++++++++++++++++++++++
# SQL connections
#+++++++++++++++++++++++++++++++
import marcpy
import marcpy.sql

import pandas
import pyodbc
import sqlalchemy

PUBconn = marcpy.connectODBC("chiefs.marc_pub.marcpub")
PUBconn
type(PUBconn)
type(PUBconn['pyodbc'])
type(PUBconn['sqlalchemy'])
type(PUBconn['details'])

sql = "SELECT * FROM CovidCaseDeathTest"
test = marcpy.getOBDCtable(PUBconn['pyodbc'], sql)
test

sql = "SELECT * FROM CovidHospital"
test2 = marcpy.getOBDCtable(PUBconn['pyodbc'], sql)
test2


marcpy.sql.dbListSchemas(PUBconn['sqlalchemy'])
marcpy.sql.dbListSchemas(PUBconn['sqlalchemy'], rmSchemaRegex=None)

marcpy.sql.dbTableStructure(PUBconn['sqlalchemy'])
marcpy.sql.dbTableStructure(PUBconn['sqlalchemy'],  addGeoIndicator=True)
marcpy.sql.dbTableStructure(PUBconn['sqlalchemy'], rmSchemaRegex=None, rmTableRegex=None)



#+++++++++++++++++++++++++++++++


#+++++++++++++++++++++++++++++++
# gitcreds
#+++++++++++++++++++++++++++++++
import marcpy

#Check if Global git credentials are set
marcpy.gitcreds.getGitConfig()

#Set them if need be
marcpy.gitcreds.setGitConfig('jacpete', "jpeterson@marc.org")



#Retrieve GitHub PAT if exists in Windows Credential Manager
marcpy.gitcreds.gitcreds_get()

#Set GitHub PAT in Windows Credential Manager
marcpy.gitcreds.gitcreds_set()

#Delete GitHub PAT in Windows Credential Manager
marcpy.gitcreds.gitcreds_delete()

#Create a PAT in GitHub (opens in your browser)
marcpy.gitcreds.gitcreds_createPAT()
#+++++++++++++++++++++++++++++++


#+++++++++++++++++++++++++++++++
# arcpy_wrappers
#+++++++++++++++++++++++++++++++
import marcpy.arcpy_wrappers

marcpy.arcpy_wrappers.Walk(workspace = "C:\\Users\\jpeterson\\Documents\\ArcGIS\\Projects\\MyProject1", datatype = "FeatureClass", pathType = 'Relative')
marcpy.arcpy_wrappers.WalkGDB('U:\\Projects\\GIS_Services')

#+++++++++++++++++++++++++++++++


#+++++++++++++++++++++++++++++++
# arcgis_wrappers
#+++++++++++++++++++++++++++++++
import marcpy.arcgis_wrappers

marcpy.arcgis_wrappers.connectArcGISOnline()
marcpy.arcgis_wrappers.connectArcGISOnline(username="jpeterson_MARC_GIS")
marcpy.arcgis_wrappers.connectArcGISOnline(username="MARC_Admin")
#+++++++++++++++++++++++++++++++


#+++++++++++++++++++++++++++++++
# anti_join
#+++++++++++++++++++++++++++++++
import marcpy
import numpy as np
import pandas as pd

npData = np.random.rand(8, 3)
TableA = pd.DataFrame(npData,
                      columns = ['A', 'B', 'C']).reset_index()
TableB = pd.DataFrame(npData[[0,1,2,3,4,7]],
                      columns = ['A', 'B', 'C']).reset_index()
marcpy.anti_join(df_left = TableA, df_right = TableB, on = ['A', 'B', 'C'])

TableC = pd.DataFrame(npData,
                      columns = ['A', 'B', 'C']).reset_index()
TableD = pd.DataFrame(npData[[0,1,2,3,4,7]],
                      columns = ['a', 'b', 'F']).reset_index()
marcpy.anti_join(df_left = TableC, df_right = TableD, on = {'A':'a', 'B':'b', 'C':'F'})
#+++++++++++++++++++++++++++++++