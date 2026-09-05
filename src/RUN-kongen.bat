@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Step 47: every form Junchen permits, priced
echo ------------------------------------------------------------
echo   Prices every combination the two characters allow, then
echo   tests the survivors against the Turkic evidence: which
echo   suffix actually existed, counted in the lexicons, and
echo   whether vowel harmony permits it.
echo.
echo   Needs step46_junchen_space.py in the same folder.
echo ==============================================================
echo.
python src\step47_kongen.py
if errorlevel 1 (
  echo.
  echo   trying the python launcher instead
  py -3 src\step47_kongen.py
)
echo.
echo   Output file: reports\step47_summary.txt
echo.
pause
