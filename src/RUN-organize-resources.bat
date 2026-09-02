@echo off
setlocal
title Organize my_resources

rem ---------------------------------------------------------------
rem  Sorts names\my_resources into:
rem    my_resources\lexicons\   source texts the pipeline parses
rem    References\             scholarship cited but not parsed
rem  Nothing is deleted. Safe to run twice: anything already filed
rem  is skipped. Wildcards are handled by move itself, so filenames
rem  with non-ASCII characters are never read into a variable.
rem ---------------------------------------------------------------

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul
set "ROOT=%CD%"
popd >nul
set "RES=%ROOT%\my_resources"
set "LEX=%RES%\lexicons"
set "REFS=%ROOT%\References"

echo.
echo   my_resources : %RES%
echo.
if not exist "%RES%" ( echo   [STOP] my_resources not found & pause & exit /b )
if not exist "%LEX%"  ( mkdir "%LEX%"  & echo   [created] my_resources\lexicons )
if not exist "%REFS%" ( mkdir "%REFS%" & echo   [created] References )
echo.

echo   --- lexicons: source texts the scripts read ----------------
call :MV "%RES%\Divanu-Lugatit-Turk-Dizini*.pdf"     "%LEX%\Divanu-Lugatit-Turk-Dizini-2MB.pdf"
call :MV "%RES%\Codex cumanicus Bibliothec*.zip"     "%LEX%\Codex_Cumanicus_Kuun_1880.zip"
call :MV "%RES%\Sir Gerard Clauson*.epub"            "%LEX%\Clauson_1972_EDPT.epub"
call :MV "%RES%\kitbalidrkllisna*.epub"              "%LEX%\AbuHayyan_Kitab_al-Idrak.epub"
call :MV "%RES%\Kutadgu Bilig Ciltli*.pdf"           "%LEX%\Kutadgu_Bilig_Kabalci_2008.pdf"
call :MV "%RES%\KUTAGU BILIG*.epub"                  "%LEX%\Kutadgu_Bilig_TDV_2018.epub"
call :MV "%RES%\Kutadgu Bilig Incelemesi*.pdf"       "%LEX%\Kutadgu_Bilig_Incelemesi_Dilacar.pdf"
call :MVDIR "%RES%\Codex Cumanicus"                  "%LEX%\Codex_Cumanicus_facsimile"
echo.

echo   --- References: scholarship cited, not parsed --------------
call :MV "%RES%\jesh-article-p121*.pdf"              "%REFS%\Esin_OSullivan_2025_Xiongnu_rulers_residences.pdf"
call :MV "%RES%\Pulleyblank - Hun Language*.html"    "%REFS%\Pulleyblank_Hun_Language_TurkicWorld.html"
call :MVDIR "%RES%\Pulleyblank - Hun Language - TurkicWorld_files" "%REFS%\Pulleyblank_Hun_Language_TurkicWorld_files"
echo.

echo   ============================================================
echo    my_resources\lexicons\ :
dir /b "%LEX%" 2>nul
echo.
echo    References\ :
dir /b "%REFS%" 2>nul
echo   ============================================================
echo.
echo   Nothing was deleted.
echo.
pause
exit /b

:MV
if exist "%~2" ( echo   [skip] %~nx2  already filed & exit /b )
dir /b "%~1" >nul 2>&1
if errorlevel 1 ( echo   [none] no match for %~nx1 & exit /b )
move "%~1" "%~2" >nul
if errorlevel 1 ( echo   [FAIL] %~nx2 ) else ( echo   [moved] %~nx2 )
exit /b

:MVDIR
if exist "%~2" ( echo   [skip] %~nx2\  already filed & exit /b )
if not exist "%~1" ( echo   [none] %~nx1\ not found & exit /b )
move "%~1" "%~2" >nul
if errorlevel 1 ( echo   [FAIL] %~nx2\ ) else ( echo   [moved] %~nx2\ )
exit /b
