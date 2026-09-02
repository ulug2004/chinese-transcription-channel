@echo off
setlocal
title Open manual downloads

echo.
echo  ============================================================
echo   Opening the resources that must be downloaded by hand
echo  ============================================================
echo.
echo   Eight browser tabs will open. Save each file into:
echo     %~dp0..\data\external
echo.
pause
echo.

echo   1/8  Baley Late Han v7 - the GOLD EVAL SET (hold it out entirely)
start "" "https://zenodo.org/records/14885154"
timeout /t 2 /nobreak >nul

echo   2/8  Schuessler Later Han + Minimal Old Chinese [CC0]
start "" "https://zenodo.org/records/14567004"
timeout /t 2 /nobreak >nul

echo   3/8  Baxter-Sagart Old Chinese v1.1 - mirror it, unlicensed personal host
start "" "https://sites.lsa.umich.edu/ocbaxtersagart/"
timeout /t 2 /nobreak >nul

echo   4/8  UW thesis - 1,040 Ming-era Uyghur terms (the only Turkic-Chinese set)
start "" "https://digital.lib.washington.edu/researchworks/items/e5c21e6f-7df6-4e19-ae9a-16231ec135c2"
timeout /t 2 /nobreak >nul

echo   5/8  Yoshida - Sogdian names in Chinese sources (negative controls)
start "" "https://www.iranicaonline.org/articles/personal-names-sogdian-1-in-chinese-sources/"
timeout /t 2 /nobreak >nul

echo   6/8  ASJP v19 CLDF - Yeniseian phonotactic prior
start "" "https://zenodo.org/records/3843469"
timeout /t 2 /nobreak >nul

echo   7/8  Unihan database (needs Unicode 16.0+ for kFanqie)
start "" "https://www.unicode.org/Public/UCD/latest/ucd/"
timeout /t 2 /nobreak >nul

echo   8/8  Secret History of the Mongols - aligned Chinese + romanized Mongolian
start "" "https://ja.wikisource.org/wiki/%%E9%%9F%%B3%%E8%%A8%%B3%%E8%%92%%99%%E6%%96%%87%%E5%%85%%83%%E6%%9C%%9D%%E7%%A7%%98%%E5%%8F%%B2"

echo.
echo   All tabs opened.
echo.
echo   Note on Zenodo: click the "Download" button next to each file.
echo   For Baxter-Sagart, the machine-readable file is the .xlsx on Dropbox -
echo   the .edu server only hosts PDFs.
echo.
pause
endlocal
