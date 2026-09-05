@echo off
setlocal
cd /d "%~dp0"
echo === step 41: the candidate space for CHANYU, priced cheapest first ===
python step41_danyu_space.py
echo.
pause
