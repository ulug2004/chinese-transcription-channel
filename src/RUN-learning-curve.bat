@echo off
setlocal
title Learning curve - how much data does this need
cd /d "%~dp0"
echo.
echo  ============================================================
echo   Learning curve: how much data does the channel need?
echo  ============================================================
echo.
echo   Trains the channel at 500 / 1k / 2k / 4k / full corpus and
echo   evaluates each on the SAME unseen chapters. Takes several
echo   minutes - it trains five models.
echo.
set "PY="
where python.exe >nul 2>&1 && set "PY=python"
if not defined PY ( where py.exe >nul 2>&1 && set "PY=py" )
if not defined PY ( where python3.exe >nul 2>&1 && set "PY=python3" )
if not defined PY (
  echo   ERROR: Python not found on PATH.
  pause
  exit /b 1
)
%PY% step10_learning_curve.py
if errorlevel 1 (
  echo.
  echo   FAILED - see the message above. Needs step 8 and step 1 output.
  pause
  exit /b 1
)
echo.
echo  ============================================================
echo   Report: reports\step10_summary.txt
echo   Data:   data\derived\learning_curve.csv
echo  ============================================================
echo.
pause
endlocal
