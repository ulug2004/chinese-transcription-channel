@echo off
setlocal
cd /d "%~dp0"
echo Building the permitted candidate space for every proposed name.
echo This reads the two lexicon CSVs and the Clauson EPUB, and writes
echo   data\derived\name_candidates.csv
echo.
python "%~dp0step21_candidates.py" %*
if errorlevel 1 (
  echo.
  echo Failed. If python is not found, try:  py "%~dp0step21_candidates.py"
)
echo.
pause
