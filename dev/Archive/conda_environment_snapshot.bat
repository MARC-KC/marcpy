@echo off

@REM set condaExe=%1
@REM set condaExeNS=%~1
set condaExe="C:\\Program Files (x86)\\Microsoft Visual Studio\\Shared\\Anaconda3_64\\Scripts\\conda.exe"
@REM set condaExe="C:\Users\jpeterson\AppData\Local\r-miniconda\Scripts\conda.exe"
set condaAct="C:\\Program Files (x86)\\Microsoft Visual Studio\\Shared\\Anaconda3_64\\Scripts\activate.bat"
@REM set condaAct="C:\Users\jpeterson\AppData\Local\r-miniconda\Scripts\Scripts\activate.bat"
@REM set condaExeNS=%condaExe:"=%

@REM set condaEnv=%1
@REM set condaEnvNS=%~1
set condaEnv="L:\\CondaEnvs\\test"
@REM set condaEnvNS=%condaEnv:"=%

@REM echo %condaExe%
@REM @REM echo %condaExeNS%
@REM echo %condaEnv%
@REM @REM echo %condaEnvNS%

set condaActivate=%condaAct% %condaEnv%
set condaExport=%condaExe% env export --prefix %condaEnv%
@REM echo %condaActivate%
@REM echo %condaExport%

%condaActivate%
cmd /C "%condaExport%"
