@echo off
setlocal
cd /d "%~dp0.."

echo.
echo ============================================================
echo   Removing References\ from the repository and its history
echo ============================================================
echo.
echo   References\ holds PDFs of published articles - JSTOR scans,
echo   journal offprints, Baxter-Sagart, Vovin, Lee et al. Those are
echo   other people's copyrighted files. They are inputs to the work,
echo   not outputs of it, and the paper's own repository listing in
echo   section 12 never included them. They must come off GitHub.
echo.
echo   The PDFs stay on your disk. Only git stops tracking them.
echo.

if not exist ".git" goto NOREPO

set "GO="
set /p "GO=Proceed? (y/n) "
if /i not "%GO%"=="y" goto ABORT
echo.

copy /y "src\_git\gitignore.txt" ".gitignore" >nul
echo   [ok] .gitignore now excludes References/

git rm -r --cached -q References 2>nul
git add -A
echo   [ok] untracked

git commit --amend --no-edit >nul
if errorlevel 1 goto AMENDFAIL
echo   [ok] commit amended - the PDFs are no longer in it
echo.

echo   Re-checking...
git ls-files > "%TEMP%\gt2.txt"
findstr /i /c:"References/" /c:"my_resources/" /c:"Downloads/" /c:"data/external/" /c:"dlt_lexicon" /c:"name_candidates" /c:"old_turkic_echo" /c:"my_notes" /c:".~lock." "%TEMP%\gt2.txt"
if errorlevel 1 echo   (nothing listed - good)
for /f %%A in ('type "%TEMP%\gt2.txt" ^| find /c /v ""') do set "NFILES=%%A"
del "%TEMP%\gt2.txt" >nul 2>&1
echo   Files now tracked: %NFILES%
echo.

set "GO2="
set /p "GO2=Force-push the corrected commit over the old one? (y/n) "
if /i not "%GO2%"=="y" goto ABORT2

git push --force-with-lease origin main
if errorlevel 1 goto PUSHFAIL
echo.
echo   [done] GitHub now has the corrected commit.
echo.
echo   Note: the old objects can linger unreferenced on GitHub for a while.
echo   The repository is private, so only you can reach them. For a
echo   guaranteed clean slate, delete the repository in Settings and run
echo   RUN-push.bat against a freshly created empty one.
goto END

:NOREPO
echo   [stop] no .git folder here.
goto END

:AMENDFAIL
echo   [stop] could not amend. Paste this window to Claude.
goto END

:ABORT
echo   Nothing changed.
goto END

:ABORT2
echo   Local commit is fixed but NOT pushed. GitHub still has the PDFs.
echo   Run this again when ready.
goto END

:PUSHFAIL
echo   Force-push failed. Paste this window to Claude.
goto END

:END
echo.
pause
