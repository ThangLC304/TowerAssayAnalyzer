@echo off
setlocal enabledelayedexpansion

set "python_version=3.9.13"
set "venv_name=TAN_env"

REM set TAN_dir to current directory
set "TAN_dir=%~dp0"

if "%OS%"=="Windows_NT" (
  set "miniconda_url=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
  set "miniconda_installer=%~dp0Miniconda3-latest-Windows-x86_64.exe"
) else (
  set "miniconda_url=https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
  set "miniconda_installer=%~dp0Miniconda3-latest-MacOSX-x86_64.sh"
)


REM if not exists anaconda or miniconda, install
if "%OS%"=="Windows_NT" (
  set "bat_found=0"

  for %%p in (
    "C:\ProgramData\miniconda3"
    "C:\ProgramData\Anaconda3"
    "C:\ProgramData\.conda"
    "%UserProfile%\miniconda3"
    "%UserProfile%\.conda"
    "%UserProfile%\Anaconda3"
  ) do (
      if exist "%%~p\Scripts\activate.bat" (
          set "conda_path=%%~p"
          set "bat_found=1"
      )
  )

  if !bat_found!==0 (
      echo Downloading Miniconda...
      powershell.exe -Command "(New-Object System.Net.WebClient).DownloadFile('%miniconda_url%', '%miniconda_installer%')"

      echo Installing Miniconda...
      start /wait "" "%miniconda_installer%" /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=%UserProfile%\miniconda3

      set "conda_path=%UserProfile%\miniconda3"
    )
  ) else (
      echo Anaconda or Miniconda already installed
  )
) else (
  if not exist "$HOME/miniconda3" (
    if not exist "$HOME/anaconda3" (
      echo Downloading Miniconda...
      curl %miniconda_url% -o %miniconda_installer%

      echo Installing Miniconda...
      chmod +x %miniconda_installer%
      bash %miniconda_installer% -b -p $HOME/miniconda3

      set "conda_path=$HOME/miniconda3"
    ) else (
      set "conda_path=$HOME/anaconda3"
    )
  ) else (
      echo Miniconda already installed

      set "conda_path=$HOME/miniconda3"
  )
)

if exist "%conda_path%\envs\%venv_name%" (
    echo %venv_name% already exists
) else (
    echo %venv_name% not found
    echo Creating virtual environment with Python %python_version%...
    if "%OS%"=="Windows_NT" (
        call %conda_path%\Scripts\conda create -n %venv_name% python==%python_version% -y
    ) else (
        $conda_path/bin/conda create -n %venv_name% python=%python_version% -y
    )
)


if "%OS%"=="Windows_NT" (
    set "activate_cmd=call %conda_path%\Scripts\activate.bat %venv_name%"
) else (
    set "activate_cmd=source $conda_path/bin/activate %venv_name%"
)


echo Activating virtual environment... at %conda_path%\envs\%venv_name%
%activate_cmd%


echo Installing TAN requirements
cd %TAN_dir%
pip install -r requirements.txt