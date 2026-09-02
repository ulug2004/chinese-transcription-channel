@echo off
setlocal
title Reading-anchored channel
cd /d "%~dp0"
echo.
echo  ============================================================
echo   Reading-anchored channel
echo  ============================================================
echo.
echo   Keys the channel on each character's reconstructed Later Han
echo   reading instead of the character itself. Reports coverage,
echo   in-domain accuracy, and - decisively - out-of-domain accuracy.
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
%PY% step11_reading_anchored.py
if errorlevel 1 (
  echo.
  echo   FAILED - see the message above.
  pause
  exit /b 1
)
echo.
echo  ============================================================
echo   Report: reports\step11_summary.txt
echo  ============================================================
echo.
pause
endlocal
