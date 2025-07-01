@echo off
setlocal EnableDelayedExpansion

REM === Network archive base directory ===
set NET_ROOT=\\10.10.60.240\aoc-storage\AVAPS\Data\Archive

REM === Get current drive letter the script is running from ===
set CURRENT_DRIVE=%~d0
set SRC_DIR=%CURRENT_DRIVE%\AVAPSdata

echo Copying FlightID folders from: %SRC_DIR%
echo To network archive: %NET_ROOT%\YYYY\

REM === Loop through all FlightID folders (20xxxxxx*) ===
for /d %%F in ("%SRC_DIR%\20??????*") do (
    set "FOLDER=%%~nxF"
    set "YEAR=!FOLDER:~0,4!"
    set "DEST_DIR=%NET_ROOT%\!YEAR!\!FOLDER!"

    echo.
    echo Copying !FOLDER! to !DEST_DIR! ...
    robocopy "%%F" "!DEST_DIR!" /E /MT:12 /dcopy:t /XO
)

echo.
echo All copies complete.
pause
