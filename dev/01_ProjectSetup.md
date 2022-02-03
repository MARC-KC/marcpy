

# Setup Python Environments

## Setup Development Envrionment
```powershell
conda create -p "CondaEnvs/marcpyDev" python=3.7 marc-kc::marcpy
conda activate "CondaEnvs/marcpyDev"

```

## Setup Production Envrionment
```powershell
conda create -p "CondaEnvs/marcpyPrd" python=3.7 marc-kc::marcpy
conda activate "CondaEnvs/marcpyPrd"
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