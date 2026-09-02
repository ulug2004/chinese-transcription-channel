@echo off
setlocal
title Steppe onomastics - dataset download
color 07

set "ROOT=%~dp0.."
set "DEST=%ROOT%\data\external"
set /a FAILED=0
set /a GOT=0

echo.
echo  ============================================================
echo   Downloading freely-licensed datasets
echo  ============================================================
echo.
echo   Destination: %DEST%
echo.

if not exist "%DEST%" mkdir "%DEST%"
if not exist "%DEST%" (
  echo   ERROR: could not create the destination folder.
  echo   Check that you have write access to this drive.
  goto :done
)

set "HAVECURL=1"
where curl.exe >nul 2>&1
if errorlevel 1 set "HAVECURL=0"

if "%HAVECURL%"=="1" (
  echo   Using curl.exe
) else (
  echo   curl.exe not found - falling back to PowerShell
)
echo.

echo  --- 1. Schuessler: Later Han + Minimal Old Chinese  [CC0] ---
echo      The Xiongnu-period phonological layer. Highest priority.
call :get "https://zenodo.org/records/14567004/files/LHantab.tsv?download=1" "LHantab.tsv" "Later Han Chinese"
call :get "https://zenodo.org/records/14567004/files/OCMtab.tsv?download=1" "OCMtab.tsv" "Minimal Old Chinese"
echo.

echo  --- 2. NTI / Fo Guang Shan Buddhist dictionary  [CC BY-SA 3.0] ---
echo      Primary training corpus: ~9,688 Sanskrit-Chinese pairs.
call :get "https://raw.githubusercontent.com/alexamies/buddhist-dictionary/master/data/dictionary/buddhist_terminology.txt" "buddhist_terminology.txt" "18,215 entries"
call :get "https://raw.githubusercontent.com/alexamies/buddhist-dictionary/master/data/dictionary/buddhist_named_entities.txt" "buddhist_named_entities.txt" "8,893 entries"
echo.

echo  --- 3. nk2028 tshet-uinh-data: Middle Chinese  [CC0] ---
rem  The path contains Chinese characters. Percent-encoding them in a .bat is
rem  unreliable ("call" eats percent signs), so PowerShell builds the URL from
rem  code points instead. Tries branch "main" then "master".
if exist "%DEST%\guangyun.csv" (
  echo      [skip]  guangyun.csv  ^(already downloaded^)
) else (
  echo      [get ]  guangyun.csv  -  Guangyun, 25,336 rows
  powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $dir=[char]0x97FB+[char]0x66F8; $fil=[char]0x5EE3+[char]0x97FB; foreach($br in @('main','master')){ $u='https://raw.githubusercontent.com/nk2028/tshet-uinh-data/'+$br+'/'+[uri]::EscapeDataString($dir)+'/'+[uri]::EscapeDataString($fil)+'.csv'; try{ Invoke-WebRequest -Uri $u -OutFile '%DEST%\guangyun.csv' -UseBasicParsing; exit 0 }catch{} }; exit 1"
  if errorlevel 1 (
    echo      [FAIL]  guangyun.csv
    set /a FAILED+=1
  ) else (
    echo      [ ok ]  guangyun.csv
    set /a GOT+=1
  )
)
echo.

echo  --- 4. DILA authority databases  [CC BY-SA 3.0] ---
echo      1,071 more Chinese-Sanskrit name pairs. Large files ^(79 MB total^).
call :get "https://raw.githubusercontent.com/DILA-edu/Authority-Databases/master/authority_person/Buddhist_Studies_Person_Authority.xml" "DILA_person_authority.xml" "49,259 persons, 611 with Sanskrit"
call :get "https://raw.githubusercontent.com/DILA-edu/Authority-Databases/master/authority_place/Buddhist_Studies_Place_Authority.xml" "DILA_place_authority.xml" "117,807 places, 460 with Sanskrit"
echo.

echo  --- 5. Unihan  [Unicode licence] ---
echo      Needs Unicode 16.0+ for the kFanqie field.
call :get "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip" "Unihan.zip" "Unihan database"
echo.

echo  ============================================================
echo   Downloaded this run: %GOT%    Failed: %FAILED%
echo  ============================================================
echo.

if %FAILED% GTR 0 (
  echo   Some downloads failed. Common causes:
  echo     - no internet connection, or a proxy/firewall in the way
  echo     - the file was renamed on the host
  echo   Run open_manual_downloads.bat to fetch them in your browser.
  echo.
)

echo   Still to get by hand ^(cannot be scripted^):
echo.
echo     * Baley Late Han v7 - the 401-item GOLD EVAL SET. Hold it out entirely.
echo         https://zenodo.org/records/14885154
echo.
echo     * Baxter-Sagart Old Chinese v1.1 - mirror it, it lives on a personal Dropbox.
echo         https://sites.lsa.umich.edu/ocbaxtersagart/
echo.
echo     * UW MA thesis, Ming-dynasty Uyghur transcriptions - 1,040 Turkic terms.
echo       The only collated Turkic-Chinese resource that exists. Extract the tables.
echo         https://digital.lib.washington.edu/researchworks/items/e5c21e6f-7df6-4e19-ae9a-16231ec135c2
echo.
echo     * Sogdian control set - hand-extract ~35 pairs from Yoshida's Iranica article.
echo         https://www.iranicaonline.org/articles/personal-names-sogdian-1-in-chinese-sources/
echo.
echo     * ASJP v19 CLDF - Yeniseian phonotactic prior.
echo         https://zenodo.org/records/3843469
echo.
echo   ^(open_manual_downloads.bat opens all of these in your browser^)
echo.

:done
echo.
echo   Contents of data\external:
echo.
if exist "%DEST%" dir /b /a-d "%DEST%" 2>nul
echo.
echo  ------------------------------------------------------------
pause
endlocal
exit /b 0


:get
rem  %~1 = url   %~2 = output filename   %~3 = description
if exist "%DEST%\%~2" (
  echo      [skip]  %~2  ^(already downloaded^)
  goto :eof
)
echo      [get ]  %~2  -  %~3
if "%HAVECURL%"=="1" (
  curl.exe -fsSL --retry 3 --connect-timeout 25 -o "%DEST%\%~2.part" "%~1"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try { [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%~1' -OutFile '%DEST%\%~2.part' -UseBasicParsing } catch { exit 1 }"
)
if errorlevel 1 (
  if exist "%DEST%\%~2.part" del /q "%DEST%\%~2.part" >nul 2>&1
  echo      [FAIL]  %~2
  echo              %~1
  set /a FAILED+=1
) else (
  move /y "%DEST%\%~2.part" "%DEST%\%~2" >nul
  echo      [ ok ]  %~2
  set /a GOT+=1
)
goto :eof
