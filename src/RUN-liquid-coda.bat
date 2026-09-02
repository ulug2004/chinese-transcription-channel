@echo off
setlocal
cd /d "%~dp0"
python "%~dp0step23_liquid_coda.py"
if errorlevel 1 echo. & echo Failed. Try:  py "%~dp0step23_liquid_coda.py"
echo.
pause
