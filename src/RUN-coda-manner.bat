@echo off
setlocal
cd /d "%~dp0"
echo === step 37: source coda class against written coda class ===
python step37_coda_manner.py
echo.
echo written: reports\step37_summary.txt
pause
