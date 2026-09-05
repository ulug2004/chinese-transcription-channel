@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Step 52: word-final consonants, and a corpus blind spot
echo ------------------------------------------------------------
echo   Three rows lean on a Chinese character writing a bare
echo   final consonant with its own vowel doing nothing. The
echo   Sanskrit corpus cannot price that, because Sanskrit words
echo   almost never end in a consonant. The Turkic corpus can.
echo.
echo   Needs step46_junchen_space.py in the same folder.
echo ==============================================================
echo.
python src\step52_final_consonant.py
if errorlevel 1 (
  echo.
  echo   trying the python launcher instead
  py -3 src\step52_final_consonant.py
)
echo.
echo   Output file: reports\step52_summary.txt
echo.
pause
