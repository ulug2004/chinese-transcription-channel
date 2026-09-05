@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Step 49: the ruling clan name, and a new measurement
echo ------------------------------------------------------------
echo   Prices the two forms of the clan name, and counts how
echo   Turkic q and k were written in Chinese, which the Later
echo   Han corpus cannot show because Sanskrit has no q.
echo.
echo   Needs step46_junchen_space.py in the same folder.
echo ==============================================================
echo.
python src\step49_clanname.py
if errorlevel 1 (
  echo.
  echo   trying the python launcher instead
  py -3 src\step49_clanname.py
)
echo.
echo   Output file: reports\step49_summary.txt
echo.
pause
