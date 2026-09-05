@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0.."

echo.
echo ============================================================
echo   Removing files that should not be in the repository
echo ============================================================
echo.

if not exist ".git" goto NOREPO

copy /y "src\_git\gitignore.txt" ".gitignore" >nul
echo   [ok] .gitignore installed

rem --- restricted sources and private notes --------------------
for %%F in (
  "data/derived/name_candidates.csv"
  "data/derived/old_turkic_echo.csv"
  "data/derived/dlt_lexicon.csv"
  "data/derived/ligeti_turkic_chinese_pairs.csv"
) do git rm --cached -q %%F 2>nul

rem --- any private note file, whatever its number ---------------
for /f "delims=" %%F in ('git ls-files ^| findstr /i /c:"my_notes"') do (
  git rm --cached -q "%%F" 2>nul
  echo   [ok] untracked %%F
)

rem --- office lock files and other stray junk -------------------
set "FOUND="
for /f "delims=" %%F in ('git ls-files ^| findstr /i /c:".~lock." /c:"~$" /c:"Thumbs.db" /c:".DS_Store"') do (
  git rm --cached -q "%%F" 2>nul
  echo   [ok] untracked %%F
  set "FOUND=1"
)
if not defined FOUND echo   [ok] no lock or junk files were tracked

git add -A
git commit --amend --no-edit >nul
if errorlevel 1 goto AMENDFAIL
echo   [ok] commit amended
echo.

git branch -M main >nul 2>&1

echo ------------------------------------------------------------
echo   Re-checking for anything that must not be pushed
echo ------------------------------------------------------------
git ls-files > "%TEMP%\gtrack.txt"
findstr /i /c:"my_resources/" /c:"Downloads/" /c:"data/external/" /c:"dlt_lexicon" /c:"name_candidates" /c:"old_turkic_echo" /c:"my_notes" /c:".~lock." "%TEMP%\gtrack.txt"
if errorlevel 1 echo   (nothing listed - good)
for /f %%A in ('type "%TEMP%\gtrack.txt" ^| find /c /v ""') do set "NFILES=%%A"
del "%TEMP%\gtrack.txt" >nul 2>&1
echo ------------------------------------------------------------
echo.
echo   Files tracked: %NFILES%
echo.
echo   If nothing was listed above, run RUN-push.bat next.
goto END

:NOREPO
echo   [stop] no .git folder here. Run RUN-git-setup.bat first.
goto END

:AMENDFAIL
echo   [stop] could not amend the commit. Paste this window to Claude.
goto END

:END
echo.
pause
