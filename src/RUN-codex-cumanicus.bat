@echo off
title Step 19 - Xiongnu readings against the Codex Cumanicus
cd /d "%~dp0.."
echo.
echo   Reads my_resources\lexicons\Codex_Cumanicus_Kuun_1880.zip
echo   Needs step16_modern_echo.py alongside it.
echo.
python "src\step19_codex_cumanicus.py"
if errorlevel 1 (
  echo.
  echo   [FAIL] see the message above
) else (
  echo.
  echo   Wrote data\derived\cuman_lexicon.csv
  echo   Wrote data\derived\cuman_echo.csv
  echo   Wrote reports\step19_summary.txt
)
echo.
pause
