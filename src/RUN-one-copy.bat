@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Remove the stray copies from the project root
echo ------------------------------------------------------------
echo   The layout is, and stays:
echo.
echo     docs\           the generated documents. Do not edit.
echo     docs\edit\      your two hand-editable copies. The build
echo                     never writes here; Claude refreshes them
echo                     after each rebuild. See its README.
echo     docsrc\         the masters Claude edits.
echo.
echo   The project root should hold neither. To be deleted:
echo     paper_EDIT.docx
echo     supplement_S1_EDIT.docx
echo     paper_submission_jdmdh.pdf
echo     supplementary_S1_candidate_readings.pdf
echo.
echo   Nothing in docs\ or docs\edit\ is touched.
echo ==============================================================
echo.

if not exist "docs\paper_submission_jdmdh.docx" goto NODOCS
if not exist "docs\edit\paper_EDIT.docx" goto NOEDIT

set "GO="
set /p "GO=Delete the four in the root? (y/n) "
if /i not "%GO%"=="y" goto ABORT
echo.

call :DEL "paper_EDIT.docx"
call :DEL "supplement_S1_EDIT.docx"
call :DEL "paper_submission_jdmdh.pdf"
call :DEL "supplementary_S1_candidate_readings.pdf"

echo.
echo ==============================================================
echo   docs\
echo ==============================================================
dir /b "docs\paper_submission*" "docs\supplementary_S1*" 2>nul
echo.
echo   docs\edit\
echo ==============================================================
dir /b "docs\edit"
echo.
echo   Git records the deletions on your next RUN-update.bat.
goto END

:DEL
if exist "%~1" (
  del /q "%~1"
  if exist "%~1" (echo   [fail] %~1 is open, close it and run again) else (echo   [ok]   deleted %~1)
) else (
  echo   [none] %~1 was not there
)
exit /b

:NODOCS
echo   [stop] docs\ is missing the paper. Nothing deleted.
goto END
:NOEDIT
echo   [stop] docs\edit\ is missing its copies. Nothing deleted.
goto END
:ABORT
echo   Nothing was deleted.
:END
echo.
pause
