@echo off
setlocal enabledelayedexpansion

set "script_path=%~dp0"
cd "%script_path%.."
set "source_folder=%script_path%"

echo Source folder: %source_folder%

pause

set "destination_folder=%userprofile%\Desktop\trajectories"

if not exist "%destination_folder%" (
    mkdir "%destination_folder%"
)

for /r "%source_folder%" %%f in (*.txt) do (
    set "relative_path=%%~dpf"
    @REM echo Relative path: !relative_path!
    set "relative_path=!relative_path:%source_folder%=!"
    @REM echo Relative path: !relative_path!
    set "target_path=%destination_folder%\!relative_path!%%~nxf"
    @REM echo Target path: !target_path!
    set "target_dir=%destination_folder%\!relative_path!"
    @REM echo Target directory: !target_dir!
    if not exist "!target_dir!" mkdir "!target_dir!"
    copy "%%f" "!target_path!"
)

echo All .txt files have been copied to %destination_folder% with their relative paths.
endlocal
pause
