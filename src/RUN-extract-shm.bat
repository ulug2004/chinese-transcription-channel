@echo off
setlocal
title Extract the Secret History corpus
cd /d "%~dp0"
echo.
echo  ============================================================
echo   Extracting the Secret History of the Mongols corpus
echo  ============================================================
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
%PY% step8_extract_shm.py
if errorlevel 1 (
  echo.
  echo   FAILED - see the message above.
  pause
  exit /b 1
)
echo.
echo  ============================================================
echo   Corpus: data\derived\shm_transcription_pairs.csv
echo   Report: reports\step8_summary.txt
echo  ============================================================
echo.
pause
endlocal
