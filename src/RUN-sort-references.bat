@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0.."

echo ==============================================================
echo   Sort the source files by whether the paper or supplement
echo   actually cites them.
echo     cited                 -^> References\
echo     not cited             -^> my_resources\unused_reference\
echo     Pulleyblank, Doerfer  -^> References\ either way, so the
echo                              volumes stay together and stay
echo                              searchable
echo   my_resources\lexicons is left exactly as it is.
echo   Nothing is deleted. Every move is checked first against
echo   src\*.py, so a file a script reads is never moved silently.
echo ==============================================================
echo.
echo   A. CITED, sitting in new_refs, to move into References
echo      Erdal, Grammar of Old Turkic                  (paper 7)
echo      Golden, Introduction to the Turkic Peoples    (paper 9)
echo      Hirth, Ancient History of China, the PDF      (paper 11)
echo      Pulleyblank 1962, Chinese translation         (paper 19)
echo      Pulleyblank 1991, Lexicon of Reconstructed    (paper 20)
echo      Schuessler 2009, Minimal Old Chinese          (paper 22)
echo      Baxter and Sagart 2014, full book             (paper 2)
echo      Tekin 1993, Irk Bitig                         (S1.14)
echo      Doerfer, TMEN, all four volumes               (S1.14)
echo.
echo   B. NOT CITED, to move to my_resources\unused_reference
echo      from References:
echo        Esin and O'Sullivan 2025, rulers' residences
echo        StarLing Yeniseian Swadesh list
echo        Yoshida, Sogdian names in Chinese
echo        references_still_needed-1.md, a stale save-collision copy
echo      from new_refs:
echo        Bonmann duplicate (References already has this paper)
echo        Hirth, the 451 KB zip; the 17.9 MB PDF is the usable one
echo        VOVIN_PART1, the 18 JSTOR page captures, now assembled
echo      from my_resources\lexicons:
echo        Kutadgu Bilig, Dilacar study, not an edition
echo        Kutadgu Bilig, TDV 2018 popular edition
echo        Abu Hayyan, Kitab al-Idrak, unreadable scan
echo.
echo   C. STAYS IN References BY YOUR RULE, though uncited
echo      Pulleyblank_Hun_Language_TurkicWorld.html and its
echo      _files folder, so all the Pulleyblank and Doerfer
echo      material sits in one searchable place
echo.
echo   NOT TOUCHED:
echo      my_resources\lexicons\Clauson, Divan, Codex, Kabalci
echo        cited, and lookup_lexicons.py reads that folder
echo ==============================================================
echo.
set "GO="
set /p "GO=Proceed? (y/n) "
if /i not "%GO%"=="y" goto ABORT
echo.

if not exist "my_resources\unused_reference" mkdir "my_resources\unused_reference"
echo   [ok]   my_resources\unused_reference ready
echo.

echo --- A. cited: new_refs to References ---
call :MV "new_refs\A Grammar of Old Turkic*" "References"
call :MV "new_refs\An Introduction to the History of the Turkic People*" "References"
call :MV "new_refs\The ancient history of China*.pdf" "References"
call :MV "new_refs\Shang Gu Han Yu*" "References"
call :MV "new_refs\Lexicon of Reconstructed Pronunciation*" "References"
call :MV "new_refs\Minimal Old Chinese*" "References"
call :MV "new_refs\Old Chinese _ A New Reconstruction*" "References"
call :MV "new_refs\Irk Bitig*" "References"
call :MV "new_refs\T*rkische und Mongolische Elemente*" "References"
call :MV "new_refs\Turkische und Mongolische Elemente*" "References"

echo.
echo --- B. not cited: into my_resources\unused_reference ---
set "U=my_resources\unused_reference"
call :MV "References\Esin_OSullivan_2025_Xiongnu_rulers_residences.pdf" "%U%"
call :MV "References\StarLing_Yeniseian_swadesh.pdf" "%U%"
call :MV "References\Yoshida_Sogdian_names_in_Chinese.pdf" "%U%"
call :MV "References\references_still_needed-1.md" "%U%"
call :MV "new_refs\Trans of the Philol Soc*" "%U%"
call :MV "new_refs\The ancient history of China*.zip" "%U%"
call :MV "my_resources\lexicons\Kutadgu_Bilig_Incelemesi_Dilacar.pdf" "%U%"
call :MV "my_resources\lexicons\Kutadgu_Bilig_TDV_2018.epub" "%U%"
call :MV "my_resources\lexicons\AbuHayyan_Kitab_al-Idrak.epub" "%U%"
if exist "new_refs\VOVIN_PART1" (
  move "new_refs\VOVIN_PART1" "%U%\" >nul 2>&1
  if errorlevel 1 (echo   [fail] VOVIN_PART1) else (echo   [ok]   VOVIN_PART1)
)

echo.
echo ==============================================================
echo   References\
echo ==============================================================
dir /b "References"
echo.
echo ==============================================================
echo   new_refs\   (empty is the goal)
echo ==============================================================
dir /b "new_refs" 2>nul
echo.
echo ==============================================================
echo   my_resources\lexicons\   (the four cited working lexicons)
echo ==============================================================
dir /b "my_resources\lexicons"
echo.
echo ==============================================================
echo   my_resources\unused_reference\
echo ==============================================================
dir /b "my_resources\unused_reference"
echo.
echo   Subfolders are not searched by the lookup steps, so anything
echo   in unused_reference is out of the search as well. Everything
echo   in References stays searchable, which is why the Pulleyblank
echo   and Doerfer files are kept there.
echo   Neither reference list changes; only where the files sit.
goto END

:MV
set "PAT=%~1"
set "DEST=%~2"
for %%F in ("%PAT%") do (
  if exist "%%~F" (
    findstr /i /m /c:"%%~nxF" src\*.py >nul 2>&1
    if not errorlevel 1 (
      echo   [skip] %%~nxF is named in a script under src\
    ) else (
      move "%%~F" "%DEST%\" >nul 2>&1
      if errorlevel 1 (echo   [fail] %%~nxF) else (echo   [ok]   %%~nxF)
    )
  )
)
exit /b

:ABORT
echo   Nothing was moved.
:END
echo.
pause
