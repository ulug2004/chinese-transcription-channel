@echo off
setlocal
title Move reference PDFs and locate the vocabulary
cd /d "%~dp0"

set "SRC=%USERPROFILE%\Downloads"
set "DST=%~dp0..\Downloads"

echo.
echo  ============================================================
echo   Moving reference PDFs into the project, then locating
echo   Ligeti's vocabulary inside the volumes
echo  ============================================================
echo.
if not exist "%DST%" mkdir "%DST%"

call :mv "ActaOrientalia_19.pdf" "Ligeti_1966_ActaOrientalia_19.pdf" "Ligeti 1966 - Sino-Uyghur vocabulary"
call :mv "ActaOrientalia_22.pdf" "Ligeti_1969_ActaOrientalia_22.pdf" "Ligeti 1969 - supplementary glossary"
call :mv "84990619.pdf"          "Shi_Shuqin_2016_gaochang_study.pdf" "Shi Shuqin 2016 - Gaochang guan zazi study"
echo.

set "PY="
where python.exe >nul 2>&1 && set "PY=python"
if not defined PY ( where py.exe >nul 2>&1 && set "PY=py" )
if not defined PY ( where python3.exe >nul 2>&1 && set "PY=python3" )
if not defined PY (
  echo   Files moved, but Python was not found - skipping the probe.
  pause
  exit /b 0
)
%PY% -c "import pdfplumber" >nul 2>&1
if errorlevel 1 (
  echo   pdfplumber not installed - skipping the probe.
  echo   Install with:  %PY% -m pip install pdfplumber
  pause
  exit /b 0
)

echo  ------------------------------------------------------------
echo   Probing - these are ~800-page volumes, so this takes
echo   several minutes per file. Leave it running.
echo  ------------------------------------------------------------
echo.
%PY% probe_ligeti.py
echo.
echo  ============================================================
echo   Report: reports\probe_ligeti.txt
echo  ============================================================
echo.
pause
endlocal
exit /b 0

:mv
if not exist "%SRC%\%~1" (
  if exist "%DST%\%~2" ( echo      [ ok ]  %~2  ^(already in project^)
  ) else ( echo      [ -- ]  %~1  NOT IN DOWNLOADS )
  goto :eof
)
if exist "%DST%\%~2" (
  echo      [skip]  %~2  ^(already in project^)
  goto :eof
)
echo      [move]  %~2  -  %~3
move /y "%SRC%\%~1" "%DST%\%~2" >nul 2>&1
if errorlevel 1 ( echo      [FAIL]  %~2 ) else ( echo      [ ok ]  %~2 )
goto :eof
