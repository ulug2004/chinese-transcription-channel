@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Push the commit that is already made
echo ------------------------------------------------------------
echo   The last run committed your work but never reached the
echo   push: git housekeeping ran first and got stuck trying to
echo   delete empty folders under .git\objects.
echo.
echo   This turns that automatic housekeeping off, then pushes.
echo   The empty folders are harmless and can stay.
echo ==============================================================
echo.

git rev-parse --git-dir >nul 2>&1
if errorlevel 1 goto NOREPO

echo   Turning off automatic housekeeping for this repository...
git config gc.auto 0
echo   [ok] it will not interrupt a push again
echo.

echo   Re-checking that nothing withheld is tracked...
git ls-files > "%TEMP%\gtrack.txt"
findstr /i /c:"my_resources/" /c:"Downloads/" /c:"data/external/" /c:"References/" /c:"dlt_lexicon" /c:"name_candidates" /c:"old_turkic_echo" /c:"my_notes" /c:".~lock" "%TEMP%\gtrack.txt" >nul
if not errorlevel 1 goto UNSAFE
del "%TEMP%\gtrack.txt" >nul 2>&1
echo   [ok] clean
echo.

echo   Local and remote before the push:
git rev-parse --short HEAD
git rev-parse --short origin/main 2>nul
echo.

git push origin main
if errorlevel 1 goto PUSHFAIL
echo.
echo   Local and remote after the push:
git rev-parse --short HEAD
git rev-parse --short origin/main
echo.
echo   [done] pushed. If those two match, it landed.
goto END

:UNSAFE
echo.
echo   [STOP] a withheld file is tracked. Nothing was pushed.
findstr /i /c:"my_resources/" /c:"Downloads/" /c:"data/external/" /c:"References/" /c:"dlt_lexicon" /c:"name_candidates" /c:"old_turkic_echo" /c:"my_notes" /c:".~lock" "%TEMP%\gtrack.txt"
del "%TEMP%\gtrack.txt" >nul 2>&1
goto END

:NOREPO
echo   [stop] this is not a git repository.
goto END

:PUSHFAIL
echo.
echo   The push failed. Copy this window and paste it to Claude.
:END
echo.
pause
