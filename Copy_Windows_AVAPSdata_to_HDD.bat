@echo off
setlocal

REM Get drive letter of the script location (e.g. E:)
set CURRENT_DRIVE=%~d0

echo Script running from drive: %CURRENT_DRIVE%

REM Copy C:\AVAPSData to <current drive>:\AVAPSData
robocopy /E /MT:12 /dcopy:t /XO "C:\AVAPSData" "%CURRENT_DRIVE%\AVAPSData"

echo Copy complete.
pause
