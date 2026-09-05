@echo off
setlocal
cd /d "%~dp0"
echo === step 43: Later Han against Old Chinese, over the record ===
echo (needs the Baxter-Sagart cache; run RUN-search-form.bat once if missing)
echo.
python step43_period_depth.py
echo.
pause
