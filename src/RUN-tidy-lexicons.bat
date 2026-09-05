@echo off
setlocal
cd /d "%~dp0.."
set "SRC=my_resources\lexicons"
set "DST=my_resources"

echo ============================================================
echo   Move the two Kutadgu Bilig files the project does not use
echo   out of my_resources\lexicons and up into my_resources
echo ------------------------------------------------------------
echo   Kutadgu_Bilig_Incelemesi_Dilacar.pdf
echo       Dilacar, a STUDY of the poem, not an edition of it
echo   Kutadgu_Bilig_TDV_2018.epub
echo       Turk Dunyasi Vakfi 2018, a popular edition, no apparatus
echo.
echo   Staying in lexicons\ :
echo   Kutadgu_Bilig_Kabalci_2008.pdf
echo       Arat's transcription and translation, Ergin index
echo ============================================================
echo.

set "N=0"
if exist "%SRC%\Kutadgu_Bilig_Incelemesi_Dilacar.pdf" set /a N+=1
if exist "%SRC%\Kutadgu_Bilig_TDV_2018.epub" set /a N+=1
if "%N%"=="0" goto NONE

set "GO="
set /p "GO=Move them? (y/n) "
if /i not "%GO%"=="y" goto ABORT
echo.

if exist "%SRC%\Kutadgu_Bilig_Incelemesi_Dilacar.pdf" (
  move /-y "%SRC%\Kutadgu_Bilig_Incelemesi_Dilacar.pdf" "%DST%\" >nul
  if errorlevel 1 (echo   [fail] Dilacar) else (echo   [ok] Dilacar moved)
)
if exist "%SRC%\Kutadgu_Bilig_TDV_2018.epub" (
  move /-y "%SRC%\Kutadgu_Bilig_TDV_2018.epub" "%DST%\" >nul
  if errorlevel 1 (echo   [fail] TDV 2018) else (echo   [ok] TDV 2018 moved)
)
echo.
echo ------------------------------------------------------------
echo   my_resources\lexicons now holds:
echo ------------------------------------------------------------
dir /b "%SRC%"
echo.
echo   Note: my_resources itself is still one of the folders the
echo   search step looks in, so these two remain searchable. If
echo   you want them out of the search as well, move them into a
echo   subfolder such as my_resources\unused - subfolders are not
echo   searched.
goto END

:NONE
echo   Neither file is in %SRC%. Nothing to do.
goto END

:ABORT
echo   Nothing was moved.

:END
echo.
pause
