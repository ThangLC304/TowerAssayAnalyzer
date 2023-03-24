@echo off

set venv_name=TAN_env
if exist "%UserProfile%\anaconda3" (
    set "conda_path = %UserProfile%\anaconda3"
) else (
    set "conda_path = %UserProfile%\Miniconda3"
)

echo Activating virtual environment...
call %conda_path%\Scripts\activate.bat %conda_path%\envs\%venv_name%

echo Run program
python main.py