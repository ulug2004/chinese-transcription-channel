@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 34 - can a written coda switch place, and can it switch manner?
echo.
python "%~dp0step34_coda_place.py"
if errorlevel 1 goto FAIL
echo.
echo   [done] see reports\step34_summary.txt
goto END
:FAIL
echo.
echo   The script failed. Paste this whole window to Claude.
:END
echo.
pause
