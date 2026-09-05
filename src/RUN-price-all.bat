@echo off
setlocal
cd /d "%~dp0.."
set NAMES_ROOT=%CD%
echo.
echo Steps 56, 57, 58.
echo   56  recover the two-character pairs the pipeline parked
echo   57  price every name by one method, on the corpus as it stands
echo   58  repair the corpus and price them all again, with deltas
echo.
python "%~dp0step56_two_character.py"
echo.
python "%~dp0step57_price_all.py"
echo.
python "%~dp0step58_fixed_corpus.py"
echo.
echo Summaries in reports\, tables in data\derived\name_prices*.csv
echo.
pause
