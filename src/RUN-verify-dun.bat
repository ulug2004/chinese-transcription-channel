@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 30 - verify the reading of dun in Mao-dun against the other books
echo.
echo   Searches Baxter-Sagart 2014 and Pulleyblank 1991 for the character,
echo   for the name in every romanisation, and for the reading itself.
echo   Allow several minutes.
echo.
python "%~dp0step30_verify_dun.py"
if errorlevel 1 goto FAIL
echo.
echo   [done] see reports\readings\verify_dun_*.txt
goto END
:FAIL
echo.
echo   The script failed. Paste this whole window to Claude.
:END
echo.
pause
