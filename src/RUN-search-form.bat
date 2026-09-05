@echo off
setlocal
cd /d "%~dp0"
if not "%~1"=="" (
  python step42_search_form.py %*
  echo.
  pause
  goto :EOF
)

:ASK
echo.
echo ============================================================
echo   Search every Turkic source on this machine for a form
echo ------------------------------------------------------------
echo   Type it in plain ASCII. The search folds the letters, so
echo     c = c-cedilla,  s = s-cedilla,  i = dotless i,
echo     n = n-tilde/eng,  and b = v = w = p are all one symbol.
echo   So  canvus  finds canvus, canbus, canwus, canpus, cangvus.
echo ============================================================
echo.
set "Q="
set /p "Q=Form to search (Enter for canvus): "
if "%Q%"=="" set "Q=canvus"
echo.
python step42_search_form.py %Q%
echo.
set "AGAIN="
set /p "AGAIN=Search another form? (y/n) "
if /i "%AGAIN%"=="y" goto ASK
echo.
echo Results are in  reports\readings\search_*.txt
pause
