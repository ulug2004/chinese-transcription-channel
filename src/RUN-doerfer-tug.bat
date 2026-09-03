@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 33 - what Doerfer says about tug, and which way the word travelled
echo.
echo   Searches the Neupersischen volumes for the headword next to the German
echo   glosses for a horsehair standard, and near entry number 969.
echo   The file is large; allow several minutes.
echo.
python "%~dp0step33_doerfer_tug.py"
if errorlevel 1 goto FAIL
echo.
echo   [done] see reports\readings\doerfer_tug.txt
goto END
:FAIL
echo.
echo   The script failed. Paste this whole window to Claude.
:END
echo.
pause
