@echo off
title Step 18 - Xiongnu readings against Divanu Lugati't-Turk
cd /d "%~dp0.."
echo.
echo   Reads my_resources\Divanu-Lugatit-Turk-Dizini-2MB.pdf
echo   Needs step16_modern_echo.py alongside it. pypdf installs automatically.
echo.
python -c "import pypdf" >NUL 2>&1
if errorlevel 1 (
  echo   installing pypdf ...
  python -m pip install --quiet pypdf
)
python "src\step18_old_turkic.py"
if errorlevel 1 (
  echo.
  echo   [FAIL] see the message above
) else (
  echo.
  echo   Wrote data\derived\dlt_lexicon.csv
  echo   Wrote data\derived\old_turkic_echo.csv
  echo   Wrote reports\step18_summary.txt
)
echo.
pause
