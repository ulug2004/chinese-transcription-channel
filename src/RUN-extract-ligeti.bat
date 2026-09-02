@echo off
setlocal
title Extract the Ligeti Turkic-Chinese corpus
cd /d "%~dp0"
echo.
echo  ============================================================
echo   Extracting Turkic-Chinese pairs from Ligeti
echo  ============================================================
echo.
echo   Reads reports\ligeti_glossary_raw.txt - fast, no PDF work.
echo.
set "PY="
where python.exe >nul 2>&1 && set "PY=python"
if not defined PY ( where py.exe >nul 2>&1 && set "PY=py" )
if not defined PY ( where python3.exe >nul 2>&1 && set "PY=python3" )
if not defined PY ( echo   ERROR: Python not found on PATH. & pause & exit /b 1 )
%PY% step12_extract_ligeti.py
if errorlevel 1 ( echo. & echo   FAILED - see above. & pause & exit /b 1 )
echo.
echo  ============================================================
echo   Corpus: data\derived\ligeti_turkic_chinese_pairs.csv
echo   Report: reports\step12_summary.txt
echo  ============================================================
echo.
pause
endlocal
