@echo off
setlocal
cd /d "%~dp0.."
set NAMES_ROOT=%CD%
echo.
echo Step 54.  The two rows that both read ulug.
echo   Wulei Ruodi        - four characters, the reading that works
echo   Huduershi Daogao   - eight characters, the reading that does not
echo.
python "%~dp0step54_ulug.py"
echo.
echo Summary written to reports\step54_summary.txt
echo.
pause
