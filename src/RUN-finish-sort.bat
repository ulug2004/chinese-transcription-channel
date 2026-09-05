@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Finish the sort: the four files the guard held back.
echo ------------------------------------------------------------
echo   All four were skipped because their names appear in
echo   src\sort_resources.py. That script does not read them: it
echo   is the importer that renames raw downloads into place, and
echo   these four are DESTINATIONS in its table, not inputs. So
echo   moving them breaks nothing. sort_resources.py has been
echo   updated so its destinations match the new layout.
echo.
echo   to my_resources\unused_reference:
echo     Esin_OSullivan_2025_Xiongnu_rulers_residences.pdf
echo     Kutadgu_Bilig_Incelemesi_Dilacar.pdf
echo     Kutadgu_Bilig_TDV_2018.epub
echo     AbuHayyan_Kitab_al-Idrak.epub
echo ==============================================================
echo.
set "GO="
set /p "GO=Proceed? (y/n) "
if /i not "%GO%"=="y" goto ABORT
echo.
set "U=my_resources\unused_reference"
if not exist "%U%" mkdir "%U%"

call :MV "References\Esin_OSullivan_2025_Xiongnu_rulers_residences.pdf"
call :MV "my_resources\lexicons\Kutadgu_Bilig_Incelemesi_Dilacar.pdf"
call :MV "my_resources\lexicons\Kutadgu_Bilig_TDV_2018.epub"
call :MV "my_resources\lexicons\AbuHayyan_Kitab_al-Idrak.epub"

echo.
echo ==============================================================
echo   my_resources\lexicons\   (should be the four cited ones)
echo ==============================================================
dir /b "my_resources\lexicons"
echo.
echo ==============================================================
echo   my_resources\unused_reference\
echo ==============================================================
dir /b "%U%"
goto END

:MV
if exist "%~1" (
  move "%~1" "my_resources\unused_reference\" >nul 2>&1
  if errorlevel 1 (echo   [fail] %~nx1) else (echo   [ok]   %~nx1)
) else (
  echo   [none] %~nx1 not there
)
exit /b

:ABORT
echo   Nothing was moved.
:END
echo.
pause
