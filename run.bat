@echo off

set venv_name=myenv

REM set TAN_dir to directory of this file
set "TAN_dir=%~dp0"

if not exist C:\ProgramData\Anaconda3\envs\%venv_name% (
    if not exist %UserProfile%\.conda\envs\%venv_name% (
        echo %venv_name% does not exist
    ) else (
        set venv_path=%UserProfile%\.conda\envs\%venv_name%
        echo %venv_name% exists at %venv_path%
    )
) else (
    set venv_path=C:\ProgramData\Anaconda3\envs\%venv_name%
    echo %venv_name% exists at %venv_path%
)

if not exist C:\ProgramData\Anaconda3\Scripts\activate.bat (
    echo Anaconda not installed
) else (
    set conda_path=C:\ProgramData\Anaconda3\Scripts\activate.bat
    echo Anaconda installed at %conda_path%
)


echo Activating virtual environment...
call %conda_path% %venv_path%
echo Virtual environment (%venv_name%) activated

echo Run program
python main.py
