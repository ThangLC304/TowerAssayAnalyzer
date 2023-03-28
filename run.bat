@echo off

set venv_name=myenv

REM set TAN_dir to directory of this file
set "TAN_dir=%~dp0"

if exist "%UserProfile%\anaconda3" (
  set "conda_path=%UserProfile%\anaconda3\Scripts"
) else (
  set "conda_path=%UserProfile%\miniconda3\Scripts"
)

for /f "tokens=*" %%a in ('%conda_path%\conda env list') do (
  for /f "tokens=1" %%b in ("%%a") do (
    if /i "%%b"=="%venv_name%" (
      echo %venv_name% already exists
    ) else (
      echo %venv_name% not found, please run setup.bat again
        exit /b 1
    )
  )
)


echo Activating virtual environment...
call %conda_path%\activate.bat %conda_path%\..\envs\%venv_name%
echo Virtual environment (%venv_name%) activated

echo Run program
python main.py
