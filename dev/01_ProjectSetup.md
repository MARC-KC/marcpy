

# Setup Python Environments

## Setup Development Envrionment
```powershell
conda create -p "CondaEnvs/marcpyDev"
conda activate "CondaEnvs/marcpyDev"
conda install python=3.7 numpy 'pandas>=1.0.0' 'keyring>=21.8.0' pyodbc sqlalchemy arcpy arcgis --channel esri
```

## Setup Production Envrionment
```powershell
conda create -p "CondaEnvs/marcpyPrd"
conda activate "CondaEnvs/marcpyPrd"
conda install python=3.7 numpy 'pandas>=1.0.0' 'keyring>=21.8.0' pyodbc sqlalchemy arcpy arcgis --channel esri
```


# Set Local VSCode Workspace Settings
```json
{
    "python.pythonPath": "${workspaceFolder}\\CondaEnvs\\marcpyDEV\\python.exe",
    "python.terminal.activateEnvironment": false,
    "python.terminal.activateEnvInCurrentTerminal": false,
}
```


# pip install git+https://github.com/MARC-KC/marcpy
# pip install -e L:\GitHub\marcpy