@echo off
setlocal
cd /d "%~dp0.."
set "REPO=chinese-transcription-channel"
set "OWNER=ulug2004"

echo.
echo ============================================================
echo   Git setup for %REPO%
echo   Repository root: %CD%
echo   GitHub owner   : %OWNER%    (private repository)
echo ============================================================
echo.

where git >nul 2>&1
if errorlevel 1 goto NOGIT

for /f "delims=" %%A in ('git config --get user.name 2^>nul') do set "GNAME=%%A"
for /f "delims=" %%A in ('git config --get user.email 2^>nul') do set "GMAIL=%%A"
if not defined GNAME goto NOIDENT
if not defined GMAIL goto NOIDENT
echo   git identity: %GNAME% ^<%GMAIL%^>
echo.

if not exist "src\_git\gitignore.txt" goto NOSUPPORT
if not exist ".gitignore" copy /y "src\_git\gitignore.txt" ".gitignore" >nul
if not exist "LICENSE" copy /y "src\_git\LICENSE" "LICENSE" >nul
if not exist "DATA_LICENSE.md" copy /y "src\_git\DATA_LICENSE.md" "DATA_LICENSE.md" >nul
echo   [ok] .gitignore, LICENSE and DATA_LICENSE.md are in place

if exist ".git" goto HAVEREPO
git init >nul
echo   [ok] initialised a new git repository
goto STAGE

:HAVEREPO
echo   [ok] this folder is already a git repository

:STAGE
git add -A
echo.
echo ------------------------------------------------------------
echo   Files git will commit
echo ------------------------------------------------------------
git status --short
echo ------------------------------------------------------------
echo.
echo   my_resources\ and Downloads\ should NOT appear above.
echo   If they do, stop and tell Claude before continuing.
echo.

set "GO="
set /p "GO=Commit these files? (y/n) "
if /i not "%GO%"=="y" goto ABORT

git commit -m "Chinese transcription channel: corpora, lexicons, models, measurements" -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
if errorlevel 1 goto NOTHING
echo   [ok] committed
echo.

where gh >nul 2>&1
if errorlevel 1 goto NOGH

set "GO2="
set /p "GO2=Create the PRIVATE GitHub repo %OWNER%/%REPO% and push? (y/n) "
if /i not "%GO2%"=="y" goto MANUAL

gh repo create %OWNER%/%REPO% --private --source=. --push
if errorlevel 1 goto GHFAIL
echo.
echo   [done] pushed to https://github.com/%OWNER%/%REPO%  (private)
goto END

:NOGIT
echo   [stop] git is not installed, or not on PATH.
echo          Install it from https://git-scm.com/download/win and run this again.
goto END

:NOIDENT
echo   [stop] git does not know who you are yet. Run these two lines, then
echo          run this file again:
echo.
echo            git config --global user.name "Aziz M. Ulug"
echo            git config --global user.email "aulug@cortechs.ai"
goto END

:NOSUPPORT
echo   [stop] src\_git\gitignore.txt is missing, so nothing was staged.
echo          Without it the commit could include my_resources\ and Downloads\.
goto END

:ABORT
echo.
echo   Nothing was committed. Files stay staged; run this again when ready,
echo   or use  git reset  to unstage them.
goto END

:NOTHING
echo   Nothing to commit - the working tree is already clean.
goto END

:NOGH
echo   The GitHub CLI (gh) is not installed, so the repo was not created.
goto MANUAL

:GHFAIL
echo.
echo   gh could not create or push the repository. Common causes: not logged
echo   in (run  gh auth login ), or the name is already taken.
goto MANUAL

:MANUAL
echo.
echo   To finish by hand:
echo     1. Create a PRIVATE repository named %REPO% at https://github.com/new
echo        Do not add a README, .gitignore or licence there.
echo     2. Then run, in this folder:
echo.
echo          git remote add origin https://github.com/%OWNER%/%REPO%.git
echo          git branch -M main
echo          git push -u origin main
goto END

:END
echo.
pause
