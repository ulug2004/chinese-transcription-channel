@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 26 - find the entries by Later Han syllable, not by character
echo.
echo   The Schuessler and Pulleyblank PDFs do not encode their Chinese
echo   characters, so step 25 found none. This searches their Latin
echo   notation instead. Allow several minutes per book.
echo.
python "%~dp0step26_lookup_roman.py"
if errorlevel 1 goto FAIL
echo.
echo   [done] see reports\readings\
goto END
:FAIL
echo.
echo   The script failed. Paste this whole window to Claude.
:END
echo.
pause
