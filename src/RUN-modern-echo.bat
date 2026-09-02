@echo off
title Step 16 - modern Turkic dictionary echoes (with null model)
cd /d "%~dp0.."
echo.
echo   Requires Turkish/Kazakh hunspell dictionaries in a folder the script can
echo   find. wordfreq is installed if missing.
echo.
python -c "import wordfreq" >NUL 2>&1
if errorlevel 1 (
  echo   installing wordfreq ...
  python -m pip install --quiet wordfreq
)
python "src\step16_modern_echo.py"
if errorlevel 1 (
  echo.
  echo   [FAIL] see the message above
) else (
  echo.
  echo   Wrote reports\step16_summary.txt
  echo   Wrote data\derived\modern_echo_candidates.csv
)
echo.
pause
