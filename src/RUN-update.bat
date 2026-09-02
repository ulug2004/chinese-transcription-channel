@echo off
setlocal
cd /d "%~dp0.."
set "REPO=chinese-transcription-channel"
set "OWNER=ulug2004"

echo.
echo ============================================================
echo   Commit and push updates to %REPO%
echo   Folder: %CD%
echo ============================================================
echo.

where git >nul 2>&1
if errorlevel 1 goto NOGIT
if not exist ".git" goto NOREPO

echo   Staging all changes...
git add -A

echo   Checking that no restricted file got staged...
git ls-files > "%TEMP%\gtrack.txt"
findstr /i /c:"my_resources/" /c:"Downloads/" /c:"data/external/" /c:"References/" /c:"dlt_lexicon" /c:"name_candidates" /c:"old_turkic_echo" /c:"my_notes" /c:".~lock" "%TEMP%\gtrack.txt" >nul
if not errorlevel 1 goto UNSAFE
echo   [ok] clean - none of the withheld files is staged
del "%TEMP%\gtrack.txt" >nul 2>&1
echo.

echo ------------------------------------------------------------
echo   Changes to be committed
echo ------------------------------------------------------------
git status --short
echo ------------------------------------------------------------
echo.

git diff --cached --quiet
if not errorlevel 1 goto NOTHING

set "GO="
set /p "GO=Commit and push these? (y/n) "
if /i not "%GO%"=="y" goto ABORT

set "MSG="
set /p "MSG=Commit message (Enter for the default): "
if not defined MSG set "MSG=Update paper, supplement and scripts"

echo.
git commit -m "%MSG%" -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
if errorlevel 1 goto CFAIL
echo   [ok] committed
echo.

git remote get-url origin >nul 2>&1
if errorlevel 1 goto NOREMOTE

git push origin main
if errorlevel 1 goto PUSHFAIL
echo.
echo   [done] pushed to https://github.com/%OWNER%/%REPO%
goto END

:NOGIT
echo   [stop] git is not installed, or not on PATH.
goto END

:NOREPO
echo   [stop] no .git folder here. Run RUN-git-setup.bat first.
goto END

:UNSAFE
echo.
echo   [STOP] a withheld file is staged. Nothing was committed or pushed.
echo          Offending entries:
echo.
findstr /i /c:"my_resources/" /c:"Downloads/" /c:"data/external/" /c:"References/" /c:"dlt_lexicon" /c:"name_candidates" /c:"old_turkic_echo" /c:"my_notes" /c:".~lock" "%TEMP%\gtrack.txt"
del "%TEMP%\gtrack.txt" >nul 2>&1
echo.
echo   Unstaging everything so nothing is committed by accident...
git reset >nul
echo   [ok] unstaged. Run RUN-fix-repo.bat, then try this again.
goto END

:NOTHING
echo   Nothing to commit - the working tree matches the last commit.
goto END

:ABORT
echo   Nothing was committed. Run  git reset  if you want to unstage.
goto END

:CFAIL
echo   The commit failed. Paste this whole window to Claude.
goto END

:NOREMOTE
echo   [stop] committed locally, but no remote origin is set. Run:
echo          git remote add origin https://github.com/%OWNER%/%REPO%.git
goto END

:PUSHFAIL
echo.
echo   The commit succeeded but the push failed. Usual causes:
echo     - sign-in was cancelled in the browser window
echo     - the remote has commits you do not have yet
echo   Paste this whole window to Claude.
goto END

:END
echo.
pause
