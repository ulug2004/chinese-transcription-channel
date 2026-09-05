@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Step 53: the Jie ethnonym, and two readings of it
echo ------------------------------------------------------------
echo   Pulleyblank and Vovin read it as Yeniseian; this supplement
echo   reads it as Turkic. Unlike Yanzhi, the character carries
echo   information bearing on the choice. This measures what a
echo   character with that vowel actually writes, and states the
echo   period objection that may outweigh the measurement.
echo.
echo   Needs step46_junchen_space.py in the same folder.
echo ==============================================================
echo.
python src\step53_jie.py
if errorlevel 1 (
  echo.
  echo   trying the python launcher instead
  py -3 src\step53_jie.py
)
echo.
echo   Output file: reports\step53_summary.txt
echo.
pause
