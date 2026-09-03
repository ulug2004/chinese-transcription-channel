@echo off
setlocal
cd /d "%~dp0.."
echo.
echo   step 32 - Pulleyblank's Lexicon on the Xiongnu words
echo.
echo   Collects every entry that names a Xiongnu context and assigns a
echo   reading, so all 40 items can be checked in one pass instead of
echo   one at a time. Allow several minutes.
echo.
python "%~dp0step32_pulleyblank_xiongnu.py"
if errorlevel 1 goto FAIL
echo.
echo   [done] see reports\step32_summary.txt
echo          and reports\readings\pulleyblank_xiongnu_blocks.txt
goto END
:FAIL
echo.
echo   The script failed. Paste this whole window to Claude.
:END
echo.
pause
