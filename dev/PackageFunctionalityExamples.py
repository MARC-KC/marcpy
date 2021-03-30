
# pip install git+https://github.com/MARC-KC/marcpy@main
# pip install -e L:\GitHub\marcpy


#+++++++++++++++++++++++++++++++
# Using Keyring and the Windows Credential Manager
#+++++++++++++++++++++++++++++++
import marcpy

marcpy.conda.list_envs()
marcpy.conda.list_packages()
marcpy.conda.env_snapshot()
marcpy.conda.env_snapshot(generalizeGitRemotes=True)

#+++++++++++++++++++++++++++++++



#+++++++++++++++++++++++++++++++
# Using Keyring and the Windows Credential Manager
#+++++++++++++++++++++++++++++++
import marcpy

marcpy.key_set(serviceName="DB_conn", userName="MARC_PRD.marcdl")
marcpy.key_get(serviceName="DB_conn", userName="MARC_PRD.marcdl")

marcpy.key_set(serviceName="DB_conn", userName="MARC_PUB.marcpub")
marcpy.key_get(serviceName="DB_conn", userName="MARC_PUB.marcpub")

marcpy.key_set(serviceName="DB_conn", userName="MARC_DEV.marcpub")
marcpy.key_get(serviceName="DB_conn", userName="MARC_DEV.marcpub")

marcpy.key_set(serviceName="DB_conn", userName="MARC_DEV.marcdl")
marcpy.key_get(serviceName="DB_conn", userName="MARC_DEV.marcdl")


# Driver={ODBC Driver 17 for SQL Server};Server=<serverName>;Database=<databaseName>;UID=<schemaName>;PWD=<password>;

# Driver={ODBC Driver 17 for SQL Server};Server=chiefs;Database=MARC_PUB;UID=marcpub;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=knights;Database=MARC_PRD;UID=marcdl;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=phantoms;Database=MARC_DEV;UID=marcpub;PWD=<password>;
# Driver={ODBC Driver 17 for SQL Server};Server=phantoms;Database=MARC_DEV;UID=marcdl;PWD=<password>;


marcpy.key_set(serviceName="", userName="API_KEY")
marcpy.key_get(serviceName="", userName="API_KEY")
marcpy.key_delete(serviceName="", userName="API_KEY")


#+++++++++++++++++++++++++++++++



#+++++++++++++++++++++++++++++++
# SQL connections
#+++++++++++++++++++++++++++++++
import marcpy

import pandas
import pyodbc

PUBconn = marcpy.sql.connectODBC("MARC_PUB.marcpub")
type(PUBconn)

sql = "SELECT * FROM CovidCaseDeathTest"
test = pandas.read_sql(sql, PUBconn)
test

sql = "SELECT * FROM CovidHospital"
test2 = pandas.read_sql(sql, PUBconn)
test2
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