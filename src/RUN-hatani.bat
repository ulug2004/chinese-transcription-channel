@echo off
setlocal
cd /d "%~dp0.."
set NAMES_ROOT=%CD%
echo.
echo Step 55.  The eight-character name cut 3-3-2.
echo   Frame 1  Hu Du Er     ha ta nyi
echo   Frame 2  Shi Dao Gao  shi dou kou
echo   A search, not a proposal.
echo.
python "%~dp0step55_hatani.py"
echo.
echo Summary written to reports\step55_summary.txt
echo.
pause
