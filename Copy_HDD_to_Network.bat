@echo off
setlocal EnableDelayedExpansion

REM === Network destination base ===
set NET_ROOT=\\10.10.60.240\aoc-storage\AVAPS\Data\Archive

REM === Get current drive letter the script is running from ===
set CURRENT_DRIVE=%~d0
set SRC_DIR=%CURRENT_DRIVE%\AVAPSdata

REM === Create log file ===
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "STAMP=%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%-%dt:~10,2%"
set LOGFILE=%SRC_DIR%\hdd_to_network_log_%STAMP%.txt

echo Copying from: %SRC_DIR% >> "%LOGFILE%"
echo Logging to:    %LOGFILE%
echo.

REM === Loop through all FlightID folders in AVAPSdata ===
for /d %%F in ("%SRC_DIR%\20??????*") do (
    set "FOLDER=%%~nxF"
    set "YEAR=!FOLDER:~0,4!"

    set DEST_DIR=%NET_ROOT%\!YEAR!\!FOLDER!
    echo Copying !FOLDER! to !DEST_DIR! ...
    echo !STAMP!: Copying !FOLDER! to !DEST_DIR! >> "%LOGFILE%"

    robocopy "%%F" "!DEST_DIR!" /E /MT:12 /dcopy:t /XO >> "%LOGFILE%"
)

echo.
echo Copy complete. Log saved to:
echo %LOGFILE%

pause
