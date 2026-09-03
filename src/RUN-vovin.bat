@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 29 - assemble Vovin 2000 Part 1 from the JSTOR page captures
echo.
python "%~dp0step29_merge_vovin.py"
if errorlevel 1 goto FAIL
echo.
echo   [done]
goto END
:FAIL
echo.
echo   The script failed. If it asks for pypdf, run:
echo       pip install pypdf
echo   Otherwise paste this whole window to Claude.
:END
echo.
pause
