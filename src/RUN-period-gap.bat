@echo off
setlocal
title Period gap - Ming to Later Han
cd /d "%~dp0"
echo.
echo  ============================================================
echo   Measuring the Ming -^> Later Han period gap
echo  ============================================================
echo.
echo   Runs in seconds - uses data already on disk, no PDFs.
echo.
set "PY="
where python.exe >nul 2>&1 && set "PY=python"
if not defined PY ( where py.exe >nul 2>&1 && set "PY=py" )
if not defined PY ( where python3.exe >nul 2>&1 && set "PY=python3" )
if not defined PY ( echo   ERROR: Python not found on PATH. & pause & exit /b 1 )
%PY% step14_period_gap.py
if errorlevel 1 ( echo. & echo   FAILED - see above. & pause & exit /b 1 )
echo.
echo  ============================================================
echo   Report: reports\step14_summary.txt
echo  ============================================================
echo.
pause
endlocal
