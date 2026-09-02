@echo off
setlocal
cd /d "%~dp0.."
set "REPO=chinese-transcription-channel"
set "OWNER=ulug2004"

echo.
echo ============================================================
echo   Push %REPO% to GitHub (private)
echo   Folder: %CD%
echo ============================================================
echo.

if not exist ".git" goto NOREPO

echo   Checking that no restricted file is tracked...
git ls-files > "%TEMP%\gtrack.txt"
findstr /i /c:"my_resources/" /c:"Downloads/" /c:"data/external/" /c:"dlt_lexicon" /c:"name_candidates" /c:"old_turkic_echo" /c:"my_notes" "%TEMP%\gtrack.txt" >nul
if not errorlevel 1 goto UNSAFE
echo   [ok] clean - none of the withheld files is tracked
for /f %%A in ('type "%TEMP%\gtrack.txt" ^| find /c /v ""') do set "NFILES=%%A"
del "%TEMP%\gtrack.txt" >nul 2>&1
echo   [ok] %NFILES% files will be pushed
echo.

git rev-parse --abbrev-ref HEAD > "%TEMP%\gbr.txt"
set /p BR=<"%TEMP%\gbr.txt"
del "%TEMP%\gbr.txt" >nul 2>&1
if /i not "%BR%"=="main" git branch -M main
echo   [ok] branch is main
echo.

git remote get-url origin >nul 2>&1
if not errorlevel 1 goto HAVEREMOTE
echo   Adding remote origin...
git remote add origin https://github.com/%OWNER%/%REPO%.git
echo   [ok] remote added
goto CONFIRM

:HAVEREMOTE
echo   [ok] remote origin already set

:CONFIRM
echo.
echo   Before continuing, the EMPTY private repository must already exist at
echo     https://github.com/%OWNER%/%REPO%
echo   created with NO README, NO .gitignore and NO licence.
echo.
set "GO="
set /p "GO=Push now? (y/n) "
if /i not "%GO%"=="y" goto ABORT

echo.
git push -u origin main
if errorlevel 1 goto PUSHFAIL
echo.
echo   [done] pushed to https://github.com/%OWNER%/%REPO%
goto END

:NOREPO
echo   [stop] no .git folder here. Run RUN-git-setup.bat first.
goto END

:UNSAFE
echo.
echo   [STOP] a withheld file is still tracked by git. Nothing was pushed.
echo          Run RUN-fix-repo.bat, then try again. Offending entries:
echo.
findstr /i /c:"my_resources/" /c:"Downloads/" /c:"data/external/" /c:"dlt_lexicon" /c:"name_candidates" /c:"old_turkic_echo" /c:"my_notes" "%TEMP%\gtrack.txt"
del "%TEMP%\gtrack.txt" >nul 2>&1
goto END

:ABORT
echo   Nothing was pushed.
goto END

:PUSHFAIL
echo.
echo   The push failed. The usual causes:
echo     - the repository does not exist yet on GitHub, or is spelled differently
echo     - it was created WITH a README, so the histories differ
echo     - sign-in was cancelled in the browser window
echo   Paste this whole window to Claude.
goto END

:END
echo.
pause
