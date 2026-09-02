@echo off
setlocal
title Turkic transfer test
cd /d "%~dp0"

echo.
echo  ============================================================
echo   Turkic transfer test
echo  ============================================================
echo.
echo   Extracts the UW thesis appendix and examples, then tests
echo   whether onset compatibility - the mechanism that worked for
echo   Sanskrit - also holds for Turkic.
echo.

set "PY="
where python.exe >nul 2>&1 && set "PY=python"
if not defined PY ( where py.exe >nul 2>&1 && set "PY=py" )
if not defined PY ( where python3.exe >nul 2>&1 && set "PY=python3" )
if not defined PY (
  echo   ERROR: Python not found on PATH.
  echo   Install from https://www.python.org/downloads/ and tick
  echo   "Add python.exe to PATH".
  echo.
  pause
  exit /b 1
)
for /f "delims=" %%V in ('%PY% --version 2^>^&1') do echo   Using %%V

rem ---- this step needs pdfplumber (the only non-stdlib dependency) ----
%PY% -c "import pdfplumber" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   This step needs the "pdfplumber" package to read the thesis PDF.
  echo   It is the only non-standard-library dependency in the project.
  echo.
  choice /c YN /m "   Install it now with pip"
  if errorlevel 2 (
    echo.
    echo   Cancelled. Install it yourself with:  %PY% -m pip install pdfplumber
    pause
    exit /b 1
  )
  echo.
  %PY% -m pip install pdfplumber
  %PY% -c "import pdfplumber" >nul 2>&1
  if errorlevel 1 (
    echo.
    echo   Install failed. Try:  %PY% -m pip install --user pdfplumber
    pause
    exit /b 1
  )
)
echo.

%PY% step_uyghur_transfer.py
if errorlevel 1 (
  echo.
  echo   FAILED - see the message above.
  pause
  exit /b 1
)

echo.
echo  ============================================================
echo   Done. See reports\step_uyghur_summary.txt for the verdict.
echo  ============================================================
echo.
pause
endlocal
