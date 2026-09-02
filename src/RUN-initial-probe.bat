@echo off
title Step 15 - initial-consonant probe (is m- ever a b-?)
cd /d "%~dp0.."
echo.
echo   Running step15_initial_probe.py ...
echo.
python "src\step15_initial_probe.py"
if errorlevel 1 (
  echo.
  echo   [FAIL] see the message above
) else (
  echo.
  echo   Wrote reports\step15_summary.txt
  echo   Wrote data\derived\initial_correspondence.csv
)
echo.
pause
