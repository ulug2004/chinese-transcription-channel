@echo off
setlocal EnableExtensions

rem  Copy the whole project off OneDrive onto the local disk.
rem  This COPIES. It deletes nothing. You delete the OneDrive copy
rem  yourself, after you have checked the new one.

for %%I in ("%~dp0..\..") do set "SRC=%%~fI"
set "DST=%USERPROFILE%\claude"

echo ==============================================================
echo   Move the project off OneDrive
echo ------------------------------------------------------------
echo   FROM  %SRC%
echo   TO    %DST%
echo.
echo   Nothing is deleted. This makes a second, local copy.
echo   Files OneDrive is holding online-only will be downloaded,
echo   so this can take a while and needs the disk space.
echo ==============================================================
echo.

echo %SRC% | find /i "OneDrive" >nul
if errorlevel 1 (
  echo   This folder is not under OneDrive already. Nothing to do.
  goto END
)

if exist "%DST%\names" (
  echo   [stop] %DST%\names already exists.
  echo   Rename or remove it first, so nothing is merged by accident.
  goto END
)

set "GO="
set /p "GO=Proceed? (y/n) "
if /i not "%GO%"=="y" goto ABORT
echo.
echo   Copying. Leave this window open.
echo.

robocopy "%SRC%" "%DST%" /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /XJ /NFL /NDL /NP
set "RC=%ERRORLEVEL%"
echo.
if %RC% GEQ 8 (
  echo   [FAILED] robocopy returned %RC%. Nothing was changed on OneDrive.
  goto END
)
echo   Copy finished, robocopy code %RC% ^(under 8 means success^).
echo.

echo ==============================================================
echo   Checking the copy
echo ==============================================================
if exist "%DST%\names\docsrc\paper.html"  (echo   [ok]   docsrc\paper.html) else (echo   [MISSING] docsrc\paper.html)
if exist "%DST%\names\src\step44_search_togri.py" (echo   [ok]   src\step44_search_togri.py) else (echo   [MISSING] src)
if exist "%DST%\names\.git"       (echo   [ok]   .git, the repository came with it) else (echo   [MISSING] .git)
if exist "%DST%\names\References" (echo   [ok]   References) else (echo   [MISSING] References)
if exist "%DST%\names\data"       (echo   [ok]   data) else (echo   [MISSING] data)
echo.

echo ==============================================================
echo   WHAT TO DO NEXT, in this order
echo ------------------------------------------------------------
echo   1. Open %DST%\names and check it looks right.
echo.
echo   2. In the Claude desktop app, connect the new folder:
echo        %DST%
echo      and disconnect the old OneDrive one. Until you do,
echo      Claude is still reading and writing the OneDrive copy.
echo.
echo   3. Run src\RUN-update.bat from the NEW folder once, to
echo      prove the repository still works from there.
echo.
echo   4. Only then delete the old folder:
echo        %SRC%
echo      Delete it in Explorer. Do not let this script do it.
echo ==============================================================
goto END

:ABORT
echo   Nothing was copied.
:END
echo.
pause
