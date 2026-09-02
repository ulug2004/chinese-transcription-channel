@echo off
setlocal
title Dump Ligeti glossary text
cd /d "%~dp0"
echo.
echo  ============================================================
echo   Dumping Ligeti's glossary text
echo  ============================================================
echo.
echo   Reads both volumes and writes the glossary pages to
echo   reports\ligeti_glossary_raw.txt. Several minutes.
echo.
set "PY="
where python.exe >nul 2>&1 && set "PY=python"
if not defined PY ( where py.exe >nul 2>&1 && set "PY=py" )
if not defined PY ( where python3.exe >nul 2>&1 && set "PY=python3" )
if not defined PY ( echo   ERROR: Python not found on PATH. & pause & exit /b 1 )
%PY% dump_ligeti_text.py
echo.
echo  ============================================================
echo   Output: reports\ligeti_glossary_raw.txt
echo  ============================================================
echo.
pause
endlocal
