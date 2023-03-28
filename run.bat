@echo off

set venv_name=TAN_env

REM set TAN_dir to directory of this file
set "TAN_dir=%~dp0"

if exist "%UserProfile%\anaconda3" (
  set "conda_path=%UserProfile%\anaconda3"
) else (
  set "conda_path=%UserProfile%\miniconda3"
)


if exist "%conda_path%\envs\%venv_name%" (
    echo %venv_name% already exists
) else (
    echo %venv_name% not found, please run setup.bat again
    pause
    exit 
    )

REM activate TAN environment
echo Activating virtual environment... at %conda_path%\envs\%venv_name%
call %conda_path%\Scripts\activate.bat %venv_name%

echo Virtual environment (%venv_name%) activated

echo Run program
python main.py
