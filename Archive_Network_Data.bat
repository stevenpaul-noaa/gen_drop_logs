@echo off
setlocal enabledelayedexpansion

set ROOT=A:\AVAPS\Data
set ARCHIVE=%ROOT%\Archive

REM All source directories
set SOURCES=%ROOT%\ACS
set SOURCES=%SOURCES% %ROOT%\Mirrors\N42\STA5\AVAPSdata
set SOURCES=%SOURCES% %ROOT%\Mirrors\N42\STA5_AUX\AVAPSdata
set SOURCES=%SOURCES% %ROOT%\Mirrors\N43\STA5\AVAPSdata
set SOURCES=%SOURCES% %ROOT%\Mirrors\N43\STA5_AUX\AVAPSdata
set SOURCES=%SOURCES% %ROOT%\Mirrors\N49\L5\AVAPSdata
set SOURCES=%SOURCES% %ROOT%\Mirrors\N49\L5_AUX\AVAPSdata
set SOURCES=%SOURCES% %ROOT%\Mirrors\N49\R5\AVAPSdata
set SOURCES=%SOURCES% %ROOT%\Mirrors\N49\R5_AUX\AVAPSdata

echo Starting copy of FlightID folders into Archive by year...

for %%S in (%SOURCES%) do (
    if exist "%%S" (
        for /d %%F in ("%%S\20??????*") do (
            set "SOURCEPATH=%%F"
            set "FLIGHTID=%%~nxF"
            set "YEAR=!FLIGHTID:~0,4!"
            set "DEST=%ARCHIVE%\!YEAR!\!FLIGHTID!"

            echo Copying from !SOURCEPATH! to !DEST!
            xcopy "!SOURCEPATH!" "!DEST!\" /E /I /D /Y >nul
        )
    ) else (
        echo Source not found: %%S
    )
)

echo Done.
pause
