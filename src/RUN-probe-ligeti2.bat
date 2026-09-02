@echo off
setlocal
title Can Ligeti's Chinese column be recovered
cd /d "%~dp0"

set "SRC=%USERPROFILE%\Downloads"
set "DST=%~dp0..\Downloads"
if not exist "%DST%" mkdir "%DST%"

echo.
echo  ============================================================
echo   Moving the two new downloads, then probing Ligeti
echo  ============================================================
echo.
call :mv "14566997.zip" "baley_final_s_companion.zip" "Baley - final -s companion data"
call :mv "yen.pdf"      "starling_yeniseian_swadesh.pdf" "StarLing Yeniseian Swadesh list"
echo.

set "PY="
where python.exe >nul 2>&1 && set "PY=python"
if not defined PY ( where py.exe >nul 2>&1 && set "PY=py" )
if not defined PY ( where python3.exe >nul 2>&1 && set "PY=python3" )
if not defined PY ( echo   ERROR: Python not found on PATH. & pause & exit /b 1 )

%PY% -c "import pypdfium2" >nul 2>&1
if errorlevel 1 (
  echo   This probe renders two page images, which needs "pypdfium2".
  choice /c YN /m "   Install it now with pip"
  if errorlevel 2 (
    echo   Continuing without page images - the text dump will still run.
  ) else (
    %PY% -m pip install pypdfium2
  )
)
echo.
echo  ------------------------------------------------------------
echo   Probing - reads both 200MB volumes, takes several minutes.
echo  ------------------------------------------------------------
echo.
%PY% probe_ligeti2.py
echo.
echo  ============================================================
echo   Report: reports\probe_ligeti2.txt
echo   Images: reports\ligeti_page_*.png
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
if exist "%DST%\%~2" ( echo      [skip]  %~2  ^(already in project^) & goto :eof )
move /y "%SRC%\%~1" "%DST%\%~2" >nul 2>&1
if errorlevel 1 ( echo      [FAIL]  %~2 ) else ( echo      [ ok ]  %~2  -  %~3 )
goto :eof
