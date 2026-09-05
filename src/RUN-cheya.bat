@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Step 48: the candidate space for Cheya, priced
echo ------------------------------------------------------------
echo   Ruodi is fixed as Inakt. This takes only the two characters
echo   in front of it, prices every form they permit, and tests
echo   the survivors against the lexicons.
echo.
echo   Needs step46_junchen_space.py in the same folder.
echo ==============================================================
echo.
python src\step48_cheya.py
if errorlevel 1 (
  echo.
  echo   trying the python launcher instead
  py -3 src\step48_cheya.py
)
echo.
echo   Output file: reports\step48_summary.txt
echo.
pause
