@echo off
setlocal
cd /d "%~dp0"
set "N=%~1"
if "%N%"=="" (
  echo.
  echo   Doerfer, Turkische und Mongolische Elemente im Neupersischen
  echo   Entry numbers used so far:  817 bahadur   969 tug
  echo   Clauson cites 818 and 828 for beg.
  echo.
  set /p "N=Entry number (Enter for 817): "
)
if "%N%"=="" set "N=817"
echo.
echo === step 36: Doerfer entry %N% across all volumes ===
python step36_doerfer_entry.py %N%
echo.
pause
