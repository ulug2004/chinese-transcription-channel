@echo off
chcp 65001 >nul
title Step 20 - how a source coda was spelled in Chinese
cd /d "%~dp0.."
python "src\step20_coda_spelling.py"
if errorlevel 1 (
  echo.
  echo   [FAIL] see the message above
) else (
  echo.
  echo   Wrote reports\step20_summary.txt
  echo   Wrote data\derived\coda_spelling.csv
)
echo.
pause
