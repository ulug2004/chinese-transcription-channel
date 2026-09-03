@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 31 - a source liquid inside a consonant cluster
echo.
echo   Measures how often a liquid before a consonant was left unwritten,
echo   which is the step the Korklu reading of gu-li asks for.
echo.
python "%~dp0step31_liquid_cluster.py"
if errorlevel 1 goto FAIL
echo.
echo   [done] see reports\step31_summary.txt
goto END
:FAIL
echo.
echo   The script failed. Paste this whole window to Claude.
:END
echo.
pause
