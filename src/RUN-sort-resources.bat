@echo off
title Sort my_resources
cd /d "%~dp0.."
python "src\sort_resources.py"
echo.
pause
