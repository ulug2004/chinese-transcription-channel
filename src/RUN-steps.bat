@echo off
setlocal
title Steppe onomastics - run analysis steps
cd /d "%~dp0"

echo.
echo  ============================================================
echo   Running analysis steps
echo  ============================================================
echo.

rem ---- find a Python interpreter ----
set "PY="
where python.exe >nul 2>&1 && set "PY=python"
if not defined PY ( where py.exe >nul 2>&1 && set "PY=py" )
if not defined PY ( where python3.exe >nul 2>&1 && set "PY=python3" )
if not defined PY (
  echo   ERROR: Python not found on PATH.
  echo.
  echo   Install it from https://www.python.org/downloads/ and tick
  echo   "Add python.exe to PATH" during setup. Nothing else is needed -
  echo   these scripts use only the Python standard library.
  echo.
  pause
  exit /b 1
)
for /f "delims=" %%V in ('%PY% --version 2^>^&1') do echo   Using %%V
echo.

echo  ------------------------------------------------------------
echo   STEP 3 - fill reconstruction columns
echo  ------------------------------------------------------------
%PY% step3_fill_reconstructions.py
if errorlevel 1 (
  echo.
  echo   STEP 3 FAILED - see the message above.
  pause
  exit /b 1
)
echo.

echo  ------------------------------------------------------------
echo   STEP 1 - build the transcription training set
echo  ------------------------------------------------------------
%PY% step1_parse_nti.py
if errorlevel 1 (
  echo.
  echo   STEP 1 FAILED - see the message above.
  pause
  exit /b 1
)
echo.

echo  ------------------------------------------------------------
echo   STEP 4 - train the transcription channel model
echo  ------------------------------------------------------------
echo   (EM over ~1,000 pairs - takes a minute or two)
%PY% step4_channel_model.py
if errorlevel 1 (
  echo.
  echo   STEP 4 FAILED - see the message above.
  echo   It needs data\derived\ from steps 1 and 3, and uyghur_chinese_pairs.csv
  echo   from RUN-uyghur.bat.
  pause
  exit /b 1
)
echo.

echo  ------------------------------------------------------------
echo   STEP 5 - competing-language comparison
echo  ------------------------------------------------------------
echo   (needs asjp-v19.1.zip in Downloads; takes a few minutes)
%PY% step5_language_comparison.py
if errorlevel 1 (
  echo.
  echo   STEP 5 FAILED - see the message above.
  pause
  exit /b 1
)
echo.

echo  ------------------------------------------------------------
echo   STEP 6 - prior adequacy experiment
echo  ------------------------------------------------------------
%PY% step6_prior_adequacy.py
if errorlevel 1 (
  echo.
  echo   STEP 6 FAILED - see the message above.
  pause
  exit /b 1
)
echo.

echo  ------------------------------------------------------------
echo   STEP 7 - ranked pronunciation reconstruction
echo  ------------------------------------------------------------
%PY% step7_reconstruct.py
if errorlevel 1 (
  echo.
  echo   STEP 7 FAILED - see the message above.
  pause
  exit /b 1
)
echo.

echo  ============================================================
echo   Done. Output written to:
echo     data\derived\    the CSVs
echo     reports\         plain-text summaries of both runs
echo  ============================================================
echo.
pause
endlocal
