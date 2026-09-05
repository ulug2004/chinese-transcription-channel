@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Step 45: OCR a book that is only page images
echo ------------------------------------------------------------
echo   Golden's Introduction to the History of the Turkic Peoples
echo   is an epub of 538 page pictures with no text in it, which
echo   is why step 44 could not search it.
echo.
echo   This reads the pictures and writes the text out, to
echo     References\<name>_OCR.txt        readable, searchable
echo     reports\_pagecache\...           so step 44 finds it too
echo.
echo   It uses tesseract if you have it, otherwise the OCR engine
echo   built into Windows. Nothing needs installing for that.
echo.
echo   538 pages takes a while. Leave the window open. You can
echo   stop it and run it again later; finished pages are kept.
echo ==============================================================
echo.
set "GO="
set /p "GO=Start? (y/n) "
if /i not "%GO%"=="y" goto ABORT
echo.
python src\step45_ocr_epub.py
if errorlevel 1 (
  echo.
  echo   trying the python launcher instead
  py -3 src\step45_ocr_epub.py
)
goto END
:ABORT
echo   Nothing was done.
:END
echo.
pause
