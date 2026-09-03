@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 28 - check the jing-lu / kingrak comparison against Hirth 1908
echo.
python "%~dp0step28_hirth.py"
if errorlevel 1 goto FAIL
echo.
echo   [done] see reports\readings\hirth_hits.txt
goto END
:FAIL
echo.
echo   The script failed. Paste this whole window to Claude.
:END
echo.
pause
