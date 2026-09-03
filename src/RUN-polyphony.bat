@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 24 - polyphonic characters in the Xiongnu record
echo.
python "%~dp0step24_polyphony.py"
if errorlevel 1 goto FAIL
echo.
echo   [done] see reports\step24_summary.txt
goto END
:FAIL
echo.
echo   The script failed. Paste this whole window to Claude.
:END
echo.
pause
