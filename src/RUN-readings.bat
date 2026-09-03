@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 25 - look up the polyphonic characters in the reference books
echo.
echo   This searches the PDFs in References\, new_refs\ and my_resources\
echo   on this computer. Nothing is uploaded. The Schuessler volume is large,
echo   so allow several minutes; progress is shown by page number.
echo.
python "%~dp0step25_lookup_readings.py"
if errorlevel 1 goto FAIL
echo.
echo   [done] extracts are in reports\readings\
echo          open reports\readings\schuessler_...txt for the character you want
goto END
:FAIL
echo.
echo   The script failed. If it says pdfplumber is missing, run:
echo       pip install pdfplumber
echo   Otherwise paste this whole window to Claude.
:END
echo.
pause
