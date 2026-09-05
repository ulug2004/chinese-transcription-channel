@echo off
setlocal
cd /d "%~dp0.."
echo ==============================================================
echo   Step 46: the candidate space for Junchen, priced
echo ------------------------------------------------------------
echo   The supplement reads this name Kunchin and defends the
echo   second character by saying voicing is leaky. Step 41, done
echo   for the other title, measured that same substitution at
echo   zero. Both cannot stand. This measures it, then asks what
echo   the characters do allow.
echo.
echo   It also uses the second reading of the character, which
echo   Schuessler tabulates and Appendix A does not print.
echo ==============================================================
echo.
python src\step46_junchen_space.py
if errorlevel 1 (
  echo.
  echo   trying the python launcher instead
  py -3 src\step46_junchen_space.py
)
echo.
echo   Output file: reports\step46_summary.txt
echo.
pause
