@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Step 50: Xuluquanqu, and what a spare character costs
echo ------------------------------------------------------------
echo   The entry reads this four-character name as Kalkan and
echo   leaves one character unaccounted. This measures how often
echo   a transcription really does use more characters than
echo   syllables, splits that figure into semantic suffixes and
echo   genuine expansion, searches the frame at each syllable
echo   count, and re-prices the reading using section 8.5.
echo.
echo   Needs step46 and step49 in the same folder.
echo ==============================================================
echo.
python src\step50_kalkan.py
if errorlevel 1 (
  echo.
  echo   trying the python launcher instead
  py -3 src\step50_kalkan.py
)
echo.
echo   Output file: reports\step50_summary.txt
echo.
pause
