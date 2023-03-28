@echo off
set miniconda_url="https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
set miniconda_installer="%~dp0Miniconda3-latest-Windows-x86_64.exe"
set python_version="3.9.13"
set venv_name="TAN_env"

REM set TAN_dir to current directory
set "TAN_dir=%~dp0"

REM if not exists anaconda or miniconda, install

if not exist "%UserProfile%\miniconda3" (
  if not exist "%UserProfile%\anaconda3" (
    echo Downloading Miniconda...
    powershell.exe -Command "(New-Object System.Net.WebClient).DownloadFile('%miniconda_url%', '%miniconda_installer%')"

    echo Installing Miniconda...
    start /wait "" "%miniconda_installer%" /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=%UserProfile%\miniconda3
  )
)

if exist "%UserProfile%\anaconda3" (
  set "conda_path=%UserProfile%\anaconda3\Scripts"
) else (
  set "conda_path=%UserProfile%\miniconda3\Scripts"
)

REM activate TAN environment
echo Activating virtual environment...
call %conda_path%\activate.bat %conda_path%\..\envs\%venv_name%

@REM REM check if git is installed
@REM where git > nul 2>nul
@REM if errorlevel 1 (
@REM     echo Installing git
@REM     C:\ProgramData\Anaconda3\\Scripts\conda.exe install -y -n %venv_name% git
@REM     echo git installed
@REM ) else (
@REM     echo git already installed
@REM )

@REM REM check if TAN_dir existed, if yes, remove
@REM if exist %TAN_dir% (
@REM     echo Removing old TAN directory
@REM     rmdir /s /q %TAN_dir%
@REM     echo Old TAN directory removed
@REM )

@REM REM clone TAN from github
@REM echo Cloning TAN from github
@REM set "TAN_repo=https://github.com/ThangLC304/TowerAssayAnalyzer"
@REM git clone %TAN_repo% %TAN_dir%

REM go to TAN directory, pip install -r -requirements.txt
echo Installing TAN requirements
cd %TAN_dir%
pip install -r requirements.txt