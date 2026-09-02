@echo off
setlocal
cd /d "%~dp0"
python "%~dp0step22_junction_merger.py"
if errorlevel 1 echo. & echo Failed. If python is not found, try:  py "%~dp0step22_junction_merger.py"
echo.
pause
