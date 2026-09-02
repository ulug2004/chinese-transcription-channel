@echo off
chcp 65001 >nul
title Lexicon lookup
cd /d "%~dp0.."
python "src\lookup_lexicons.py" %*
echo.
pause
