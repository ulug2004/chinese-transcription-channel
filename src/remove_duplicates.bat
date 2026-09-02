@echo off
setlocal
title Remove duplicate downloads

set "PROJ=%~dp0.."
set "DL=%PROJ%\Downloads"
set "EXT=%PROJ%\data\external"
set "WINDL=%USERPROFILE%\Downloads"
set /a NDEL=0
set /a NKEPT=0

echo.
echo  ============================================================
echo   Remove duplicates - files already in data\external
echo  ============================================================
echo.
echo   A file is deleted ONLY if a file with the same name AND the
echo   same exact byte size exists in data\external.
echo   Anything else is left alone.
echo.

if not exist "%EXT%" (
  echo   ERROR: data\external not found. Run download_data.bat first.
  goto :finish
)

rem ---------- pass 1: report ----------
echo   ---- Scanning project Downloads folder ----
set "MODE=DRYRUN"
if exist "%DL%" (
  for %%F in ("%DL%\*") do call :dedup "%DL%" "%%~nxF" %%~zF
) else (
  echo      project Downloads folder not found - skipping
)
echo.
echo   ---- Scanning Windows Downloads folder ----
if exist "%WINDL%" (
  for %%F in ("%WINDL%\*") do call :dedup "%WINDL%" "%%~nxF" %%~zF
)
echo.

if %NDEL%==0 (
  echo   Nothing to remove - no exact duplicates found.
  goto :finish
)

echo  ------------------------------------------------------------
echo   %NDEL% duplicate^(s^) found. They will be DELETED.
echo   The copies in data\external are kept.
echo  ------------------------------------------------------------
echo.
choice /c YN /m "   Delete them now"
if errorlevel 2 (
  echo.
  echo   Cancelled. Nothing was deleted.
  goto :finish
)
echo.

rem ---------- pass 2: delete ----------
set /a NDEL=0
set "MODE=DELETE"
echo   ---- Deleting ----
if exist "%DL%"    for %%F in ("%DL%\*")    do call :dedup "%DL%" "%%~nxF" %%~zF
if exist "%WINDL%" for %%F in ("%WINDL%\*") do call :dedup "%WINDL%" "%%~nxF" %%~zF
echo.
echo   Deleted: %NDEL%

:finish
echo.
echo   Files kept in data\external:
echo.
if exist "%EXT%" dir /b /a-d "%EXT%" 2>nul
echo.
echo  ------------------------------------------------------------
pause
endlocal
exit /b 0


:dedup
rem  %~1 = folder   %~2 = filename   %~3 = size in that folder
if not exist "%EXT%\%~2" goto :eof
rem  never compare data\external against itself
if /i "%~1"=="%EXT%" goto :eof
set "S2="
for %%G in ("%EXT%\%~2") do set "S2=%%~zG"
if not "%~3"=="%S2%" (
  echo      [keep]  %~2  -  sizes differ ^(%~3 vs %S2%^), not a duplicate
  set /a NKEPT+=1
  goto :eof
)
if "%MODE%"=="DRYRUN" (
  echo      [dup ]  %~2  ^(%~3 bytes^)  in  %~1
  set /a NDEL+=1
  goto :eof
)
del /q "%~1\%~2" >nul 2>&1
if errorlevel 1 (
  echo      [FAIL]  %~2  -  could not delete
) else (
  echo      [ del]  %~2
  set /a NDEL+=1
)
goto :eof
