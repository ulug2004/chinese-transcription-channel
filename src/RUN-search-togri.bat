@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Step 44: find a source for the *togri reading of Tu-qi.
echo ------------------------------------------------------------
echo   Section 9.1 of the paper says the Turkic-hypothesis
echo   literature reads this title as *togri, and cites nobody.
echo   This searches every PDF and EPUB in References,
echo   my_resources and new_refs for a page that carries both
echo   the Chinese title and a Turkic togri form, which is what
echo   somebody proposing the equation would look like.
echo.
echo   The first run extracts the text of every book and may take
echo   several minutes. It is cached, so later runs are fast.
echo ==============================================================
echo.
python src\step44_search_togri.py
if errorlevel 1 (
  echo.
  echo   python not found on the PATH, trying the launcher
  py -3 src\step44_search_togri.py
)
echo.
echo   Output file: reports\readings\search_togri.txt
echo.
pause
