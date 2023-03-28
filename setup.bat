@echo off
set "miniconda_url=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
set "miniconda_installer=%~dp0Miniconda3-latest-Windows-x86_64.exe"
set "python_version=3.9.13"
set "venv_name=TAN_env"

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
) else (
    echo Anaconda or Miniconda already installed
)

if exist "%UserProfile%\anaconda3\Scripts\conda.exe" (
  set "conda_path=%UserProfile%\anaconda3"
) else (
  set "conda_path=%UserProfile%\miniconda3"
)

if exist "%conda_path%\envs\%venv_name%" (
    echo %venv_name% already exists
) else (
    echo %venv_name% not found
    echo Creating virtual environment with Python %python_version%...
    call %conda_path%\Scripts\conda create -n %venv_name% python==%python_version% -y
    )
  )
)


REM activate TAN environment
echo Activating virtual environment... at %conda_path%\envs\%venv_name%
call %conda_path%\Scripts\activate.bat %venv_name%


REM go to TAN directory, pip install -r -requirements.txt
echo Installing TAN requirements
cd %TAN_dir%
pip install -r requirements.txt