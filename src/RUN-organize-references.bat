@echo off
setlocal
title Organize project references

rem ---------------------------------------------------------------
rem  Collects the cited sources into names\References
rem  - MOVES reference PDFs out of %USERPROFILE%\Downloads
rem  - COPIES reference PDFs out of names\Downloads
rem    (copied, not moved, because src\*.py read some of the PDFs in
rem     names\Downloads by path - moving them would break the pipeline)
rem  Safe to run more than once: anything already filed is skipped.
rem ---------------------------------------------------------------

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul
set "ROOT=%CD%"
popd >nul

set "REFS=%ROOT%\References"
set "PROJDL=%ROOT%\Downloads"
set "USERDL=%USERPROFILE%\Downloads"

echo.
echo   Project root : %ROOT%
echo   References   : %REFS%
echo.

if not exist "%REFS%" (
    mkdir "%REFS%"
    echo   [created] References\
) else (
    echo   [reusing] References\
)
echo.

echo   --- moving from %USERDL% -----------------------------------
call :MOVEONE "%USERDL%\early-nomads-of-the-eastern-steppe*.pdf"       "Savelyev_Jeong_2020_early_nomads_eastern_steppe.pdf"
call :MOVEONE "%USERDL%\sciadv.adf3904*.pdf"                           "Lee_2023_Xiongnu_genetic_population_structure.pdf"
call :MOVEONE "%USERDL%\Trans of the Philol Soc*Bonmann*.pdf"          "Bonmann_2025_Xiongnu_Huns_Paleo_Siberian.pdf"
echo.

echo   --- copying from names\Downloads ---------------------------
call :COPYONE "%PROJDL%\baley_late_han_v7_description.pdf"             "Baley_2025_late_han_v7_description.pdf"
call :COPYONE "%PROJDL%\BaxterSagart_by_radical_stroke.pdf"            "BaxterSagart_2014_by_radical_stroke.pdf"
call :COPYONE "%PROJDL%\starling_yeniseian_swadesh.pdf"                "StarLing_Yeniseian_swadesh.pdf"
call :COPYONE "%PROJDL%\yoshida_sogdian_names_in_chinese.pdf"          "Yoshida_Sogdian_names_in_Chinese.pdf"
echo.

echo   --- left in place (scripts read these by path) -------------
call :NOTE "%PROJDL%\Ligeti_1966_ActaOrientalia_19.pdf"                "ref 10  - dump_ligeti_text.py, probe_ligeti.py"
call :NOTE "%PROJDL%\Ligeti_1969_ActaOrientalia_22.pdf"                "ref 11  - dump_ligeti_text.py, probe_ligeti.py"
call :NOTE "%PROJDL%\UW_thesis_Ming_Uyghur_transcriptions.pdf"         "ref 16  - step_uyghur_transfer.py"
call :NOTE "%PROJDL%\Shi_Shuqin_2016_gaochang_study.pdf"               "context - probe_ligeti.py"
echo.

echo   ============================================================
echo    References\ now contains:
echo   ============================================================
dir /b "%REFS%"
echo.
echo   Done. Nothing was deleted.
echo.
pause
exit /b

rem --- move one wildcard-matched file, renaming it in the same step ---
rem  Do NOT use  for %%F in (%~1)  here: an unquoted path containing
rem  spaces gets split into separate tokens and the wildcard never
rem  matches. Letting move expand the wildcard also keeps non-ASCII
rem  filenames out of variables, where the console codepage mangles them.
:MOVEONE
if exist "%REFS%\%~2" ( echo   [skip] %~2  already in References & exit /b )
dir /b "%~1" >nul 2>&1
if errorlevel 1 ( echo   [none] no match for %~nx1 & exit /b )
move "%~1" "%REFS%\%~2" >nul
if errorlevel 1 ( echo   [FAIL] %~2 ) else ( echo   [moved] %~2 )
exit /b

:COPYONE
if not exist "%~1" ( echo   [none] %~nx1 not in names\Downloads & exit /b )
if exist "%REFS%\%~2" ( echo   [skip] %~2  already in References & exit /b )
copy /y "%~1" "%REFS%\%~2" >nul
if errorlevel 1 ( echo   [FAIL] %~2 ) else ( echo   [copied] %~2 )
exit /b

:NOTE
if exist "%~1" ( echo   [keep] %~nx1  ^| %~2 ) else ( echo   [gone] %~nx1 )
exit /b
