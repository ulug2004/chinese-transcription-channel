@echo off
setlocal
cd /d "%~dp0"
echo === step 35: which source vowel does a Later Han central vowel write ===
python step35_vowel_bogu_baga.py > "..\reports\step35_summary.txt" 2>&1
type "..\reports\step35_summary.txt"
echo.
echo written: reports\step35_summary.txt
pause
