@echo off
set "miniconda_url=https://repo.continuum.io/miniconda/Miniconda3-latest-Windows-x86_64.exe"
set "miniconda_installer=%~dp0Miniconda3-lastest-Windows-x86_64.exe"
set "python_version=3.9.13"
set "venv_name=TAN_env"

set TAN_dir = C:\TowerAssayAnalyzer

REM if not exists anaconda or miniconda, install

if not exist %UserProfile%\Miniconda3\Scripts\conda.exe (
    echo Installing Miniconda3
    echo Downloading Miniconda3
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%miniconda_url%', '%miniconda_installer%')"
    echo Installing Miniconda3
    %miniconda_installer% /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniconda3
    echo Miniconda3 installed
    echo Installing TAN environment
    %UserProfile%\Miniconda3\Scripts\conda.exe create -y -n %venv_name% python=%python_version%
    echo TAN environment installed
    echo Removing Miniconda3 installer
    del %miniconda_installer%
    echo Miniconda3 installer removed
)

REM activate TAN environment
call %UserProfile%\Miniconda3\Scripts\activate.bat %venv_name%

REM check if git is installed
where git > nul 2>nul
if errorlevel 1 (
    echo Installing git
    %UserProfile%\Miniconda3\Scripts\conda.exe install -y -n %venv_name% git
    echo git installed
) else (
    echo git already installed
)

REM check if TAN_dir existed, if yes, remove
if exist %TAN_dir% (
    echo Removing old TAN directory
    rmdir /s /q %TAN_dir%
    echo Old TAN directory removed
)

REM clone TAN from github
echo Cloning TAN from github
set "TAN_repo=https://github.com/ThangLC304/TowerAssayAnalyzer"
git clone %TAN_repo% %TAN_dir%

REM go to TAN directory, pip install -r -requirements.txt
echo Installing TAN requirements
cd %TAN_dir%
pip install -r requirements.txt