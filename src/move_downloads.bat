@echo off
setlocal
title Move downloaded datasets into the project

set "SRC=%USERPROFILE%\Downloads"
set "DST=%~dp0..\Downloads"
set /a MOVED=0
set /a ABSENT=0

echo.
echo  ============================================================
echo   Moving downloaded datasets into the project
echo  ============================================================
echo.
echo   From: %SRC%
echo   To:   %DST%
echo.

if not exist "%SRC%" (
  echo   ERROR: Downloads folder not found at %SRC%
  goto :finish
)
if not exist "%DST%" mkdir "%DST%"

echo  --- Schuessler reconstructions [CC0] ---
call :mv "LHantab.tsv" "LHantab.tsv" "Later Han Chinese - the Xiongnu-period layer"
call :mv "OCMtab.tsv" "OCMtab.tsv" "Minimal Old Chinese"
echo.

echo  --- Baley Late Han v7 - GOLD EVAL SET [CC BY 4.0] ---
call :mv "chinese_transcription_of_buddhist_terms_late_han + gandhari IPA + OC.csv" "baley_late_han_v7.csv" "401 entries, reconstructions both sides"
call :mv "CHANGELOG.txt" "baley_late_han_v7_CHANGELOG.txt" "Baley changelog"
call :mv "Dataset Description.pdf" "baley_late_han_v7_description.pdf" "Baley dataset description"
echo.

echo  --- Turkic and control sets ---
call :mv "Tan_washington_0250O_20375.pdf" "UW_thesis_Ming_Uyghur_transcriptions.pdf" "1,040 Uyghur terms - ONLY Turkic-Chinese source"
call :mv "personal-names-sogdian-i-in-chinese-sources.pdf" "yoshida_sogdian_names_in_chinese.pdf" "Sogdian negative controls"
call :mv "asjp-v19.1.zip" "asjp-v19.1.zip" "Yeniseian phonotactic prior"
echo.

echo  --- Secret History of the Mongols ---
if exist "%SRC%\*.epub" (
  move /y "%SRC%\*.epub" "%DST%\" >nul 2>&1
  if errorlevel 1 (
    echo      [FAIL]  .epub  - could not move
  ) else (
    echo      [ ok ]  Secret History of the Mongols ^(.epub^)
    set /a MOVED+=1
  )
) else (
  echo      [ -- ]  no .epub found in Downloads
  set /a ABSENT+=1
)
echo.

echo  --- Baxter-Sagart ---
call :mv "BaxterSagartOC2015-10-13.xlsx" "BaxterSagartOC2015-10-13.xlsx" "THE machine-readable one - ~5,000 items"
call :mv "OCNR-errata-2020-10-20_LS_WB_final-1.xlsx" "BaxterSagart_errata_2020-10-20.xlsx" "corrections through Oct 2020"
call :mv "BaxterSagartOCbyRadStr2014-09-20.pdf" "BaxterSagart_by_radical_stroke.pdf" "the PDF - reference only, not data"
echo.

echo  ============================================================
echo   Moved: %MOVED%    Not found: %ABSENT%
echo  ============================================================
echo.
echo   STILL MISSING - run download_data.bat to get these:
echo.
echo     * buddhist_terminology.txt      NTI dictionary  ^<-- PRIMARY TRAINING CORPUS
echo     * buddhist_named_entities.txt   NTI named entities
echo     * guangyun.csv                  Middle Chinese, 25,336 rows
echo     * Unihan.zip                    kFanqie field
echo.
echo   AND download by hand:
echo.
echo     * Baxter-Sagart .XLSX - you have the PDF, which is not machine-readable.
echo       The .xlsx is the Dropbox link on:
echo         https://sites.lsa.umich.edu/ocbaxtersagart/
echo.
echo   ALSO: there is a 944 MB "Unconfirmed 296605.crdownload" in your Downloads -
echo   an interrupted browser download. Left untouched. Delete it if you do not
echo   know what it was.
echo.

:finish
echo.
echo   Contents of the project Downloads folder:
echo.
if exist "%DST%" dir /b /a-d "%DST%" 2>nul
echo.
echo  ------------------------------------------------------------
pause
endlocal
exit /b 0


:mv
rem  %~1 = source filename   %~2 = destination filename   %~3 = description
if not exist "%SRC%\%~1" (
  echo      [ -- ]  %~2  NOT IN DOWNLOADS
  set /a ABSENT+=1
  goto :eof
)
if exist "%DST%\%~2" (
  echo      [skip]  %~2  ^(already in project^)
  goto :eof
)
move /y "%SRC%\%~1" "%DST%\%~2" >nul 2>&1
if errorlevel 1 (
  echo      [FAIL]  %~2
) else (
  echo      [ ok ]  %~2  -  %~3
  set /a MOVED+=1
)
goto :eof
