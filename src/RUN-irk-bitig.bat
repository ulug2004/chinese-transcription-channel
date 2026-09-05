@echo off
setlocal
cd /d "%~dp0"
echo === step 40: extract a ninth-century word list from the Irk Bitig ===
python step40_irk_bitig.py
echo.
pause
