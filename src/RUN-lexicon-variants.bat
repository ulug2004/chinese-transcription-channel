@echo off
title Step 17 - lexicon variants (loanword filter, union vs intersection)
cd /d "%~dp0.."
echo.
echo   Needs step16_modern_echo.py alongside it and the hunspell dictionaries.
echo   wordfreq is installed if missing.
echo.
python -c "import wordfreq" >NUL 2>&1
if errorlevel 1 (
  echo   installing wordfreq ...
  python -m pip install --quiet wordfreq
)
python "src\step17_lexicon_variants.py"
if errorlevel 1 (
  echo.
  echo   [FAIL] see the message above
) else (
  echo.
  echo   Wrote reports\step17_summary.txt
  echo   Wrote data\derived\lexicon_variants.csv
)
echo.
pause
