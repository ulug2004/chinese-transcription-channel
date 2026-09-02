@echo off
setlocal
title Chinese to Turkic channel
cd /d "%~dp0"
echo.
echo  ============================================================
echo   Chinese -^> Turkic channel, trained in-domain
echo  ============================================================
echo.
set "PY="
where python.exe >nul 2>&1 && set "PY=python"
if not defined PY ( where py.exe >nul 2>&1 && set "PY=py" )
if not defined PY ( where python3.exe >nul 2>&1 && set "PY=python3" )
if not defined PY ( echo   ERROR: Python not found on PATH. & pause & exit /b 1 )
%PY% step13_turkic_channel.py
if errorlevel 1 ( echo. & echo   FAILED - needs step 12 output. & pause & exit /b 1 )
echo.
echo  ============================================================
echo   Report: reports\step13_summary.txt
echo  ============================================================
echo.
pause
endlocal
