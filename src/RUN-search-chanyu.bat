@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo   The three searches for the CHANYU question, in one go
echo     canvus   the proposed archaic form, with -n
echo     camvus   the same on the -m route (26 percent)
echo     cavus    the control: the word that IS attested
echo ------------------------------------------------------------
echo   The first run extracts Doerfer, Kutadgu Bilig and Clauson
echo   and caches them. That takes a few minutes, once.
echo ============================================================
echo.
python step42_search_form.py canvus
echo.
echo ------------------------------------------------------------
echo.
python step42_search_form.py camvus
echo.
echo ------------------------------------------------------------
echo.
python step42_search_form.py cavus
echo.
echo ============================================================
echo   Done. Three files written:
echo     reports\readings\search_canvus.txt
echo     reports\readings\search_camvus.txt
echo     reports\readings\search_cavus.txt
echo   Tell Claude they are ready; no need to paste them.
echo ============================================================
pause
