@echo off
setlocal
title Segmental channel on the Secret History corpus
cd /d "%~dp0"
echo.
echo  ============================================================
echo   Segmental channel - trained on the Secret History corpus
echo  ============================================================
echo.
echo   This is the experiment that separates "the method is wrong"
echo   from "1,017 pairs was not enough data". Takes a few minutes.
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
%PY% step9_segmental_channel.py
if errorlevel 1 (
  echo.
  echo   FAILED - see the message above. Needs step 8 output
  echo   ^(data\derived\shm_transcription_pairs.csv^).
  pause
  exit /b 1
)
echo.
echo  ============================================================
echo   Report: reports\step9_summary.txt
echo  ============================================================
echo.
pause
endlocal
