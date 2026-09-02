@echo off
setlocal
title Probe the Secret History epub
cd /d "%~dp0"
echo.
echo  ============================================================
echo   Probing the Secret History of the Mongols epub
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
%PY% probe_shm.py
echo.
echo  ============================================================
echo   Report: reports\probe_shm.txt
echo  ============================================================
echo.
pause
endlocal
