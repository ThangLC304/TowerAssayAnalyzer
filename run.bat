@echo off

set venv_name=TAN_env

REM set TAN_dir to directory of this file
set "TAN_dir=%~dp0"

REM check if anaconda or miniconda is installed, C:\ProgramData\Anaconda3\Scripts\conda.exe
if not exist C:\ProgramData\Anaconda3\Scripts\conda.exe (
    echo Anaconda or Miniconda is not installed
    echo Please install Anaconda or Miniconda
    echo Exiting...
    pause
    exit
) else (
    echo Anaconda or Miniconda is installed
    set conda_path=C:\ProgramData\Anaconda3
)

echo Activating virtual environment...
echo Accessing virtual environment at path: %conda_path%\envs\%venv_name%
call %conda_path%\Scripts\activate.bat %conda_path%\envs\%venv_name%
echo Virtual environment (%venv_name%) activated

echo Run program
python main.py

pause