@echo off
setlocal
cd /d "%~dp0"
set N=%1
if "%N%"=="" set N=817
echo === step 36: Doerfer entry %N% across all volumes ===
python step36_doerfer_entry.py %N%
echo.
pause
