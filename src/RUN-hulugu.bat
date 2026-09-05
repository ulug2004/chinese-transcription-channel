@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Step 51: Hulugu, and two objections its entry gets wrong
echo ------------------------------------------------------------
echo   The entry says one segment is unwritable and another is
echo   discarded. Neither holds: a liquid coda left open is the
echo   majority spelling, and a written coda usually writes the
echo   onset of the next syllable. This counts both and prices
echo   the reading using section 8.5.
echo.
echo   Needs step46 and step49 in the same folder.
echo ==============================================================
echo.
python src\step51_kurluga.py
if errorlevel 1 (
  echo.
  echo   trying the python launcher instead
  py -3 src\step51_kurluga.py
)
echo.
echo   Output file: reports\step51_summary.txt
echo.
pause
