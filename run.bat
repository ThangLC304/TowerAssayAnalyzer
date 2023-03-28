@echo off

set venv_name=TAN_env

REM set TAN_dir to directory of this file
set "TAN_dir=%~dp0"

if "%OS%"=="Windows_NT" (
  set "conda_path=%UserProfile%\miniconda3"
  set "activate_cmd=call %conda_path%\Scripts\activate.bat %venv_name%"
) else (
  set "conda_path=$HOME/miniconda3"
  set "activate_cmd=source $conda_path/bin/activate %venv_name%"
)

if exist "%conda_path%\envs\%venv_name%" (
    echo %venv_name% already exists
) else (
    echo %venv_name% not found, please run setup.bat again
    if "%OS%"=="Windows_NT" (
      set /p _=Press any key to continue...
    ) else (
      read -p "Press [Enter] key to continue..."
    )
    exit 
    )

REM activate TAN environment
echo Activating virtual environment...
%activate_cmd%

echo Virtual environment (%venv_name%) activated

echo Running program...
python main.py

if "%OS%"=="Windows_NT" pause
else read -p "Press [Enter] key to continue..."