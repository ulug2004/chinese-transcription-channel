@echo off
title Finish moving the Bonmann PDF

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul
set "ROOT=%CD%"
popd >nul
set "REFS=%ROOT%\References"
set "USERDL=%USERPROFILE%\Downloads"
set "TARGET=Bonmann_2025_Xiongnu_Huns_Paleo_Siberian.pdf"

echo.
if exist "%REFS%\%TARGET%" (
    echo   [skip] %TARGET% is already in References
    goto :done
)

rem move handles the wildcard itself, so the filename - which contains
rem non-ASCII characters - is never read into a variable, and the space
rem splitting that broke the previous run cannot happen.
move "%USERDL%\Trans of the Philol Soc*Bonmann*.pdf" "%REFS%\%TARGET%" >nul
if errorlevel 1 (
    echo   [FAIL] not moved - check that it is still in %USERDL%
) else (
    echo   [moved] %TARGET%
)

:done
echo.
echo   References\ now contains:
echo.
dir /b "%REFS%\*.pdf"
echo.
pause
