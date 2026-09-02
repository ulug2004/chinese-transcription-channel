@echo off
setlocal enabledelayedexpansion
title Dataset status

set "DEST=%~dp0..\data\external"

echo.
echo  ============================================================
echo   Dataset status
echo  ============================================================
echo.
echo   Looking in: %DEST%
echo.

if not exist "%DEST%" (
  echo   Folder does not exist yet - run download_data.bat first.
  echo.
  pause
  exit /b 0
)

call :chk "LHantab.tsv"                 "Schuessler Later Han          [CC0]      REQUIRED"
call :chk "OCMtab.tsv"                  "Schuessler Minimal Old Chinese[CC0]"
call :chk "buddhist_terminology.txt"    "NTI terminology               [CC BY-SA] REQUIRED"
call :chk "buddhist_named_entities.txt" "NTI named entities            [CC BY-SA]"
call :chk "guangyun.csv"                "Guangyun / Middle Chinese     [CC0]"
call :chk "Unihan.zip"                  "Unihan database               [Unicode]"

echo.
echo   -- manual downloads --
call :chkany "*johd*"    "Baley Late Han v7 - GOLD EVAL SET"
call :chkany "*axter*"   "Baxter-Sagart Old Chinese v1.1"
call :chkany "*asjp*"    "ASJP v19 - Yeniseian prior"

echo.
echo  ------------------------------------------------------------
echo.
pause
endlocal
exit /b 0

:chk
if exist "%DEST%\%~1" (
  for %%A in ("%DEST%\%~1") do set "SZ=%%~zA"
  echo    [ ok ]  %~2
  echo            %~1  ^(!SZ! bytes^)
) else (
  echo    [ -- ]  %~2
  echo            %~1  MISSING
)
goto :eof

:chkany
set "FOUND="
for %%F in ("%DEST%\%~1") do set "FOUND=%%~nxF"
if defined FOUND (
  echo    [ ok ]  %~2  -  !FOUND!
) else (
  echo    [ -- ]  %~2  -  not found
)
goto :eof
