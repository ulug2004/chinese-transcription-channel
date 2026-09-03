@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 27 - pull Schuessler's entries out through the OCR
echo.
echo   Searches by the tag MHan and by Mandarin syllable, which survive
echo   the OCR, instead of by reconstruction, which does not.
echo   Allow several minutes.
echo.
python "%~dp0step27_schuessler_entries.py"
if errorlevel 1 goto FAIL
echo.
echo   [done] see reports\readings\schuessler_MHan.txt
goto END
:FAIL
echo.
echo   The script failed. Paste this whole window to Claude.
:END
echo.
pause
