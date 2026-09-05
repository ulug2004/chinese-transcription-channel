# -*- coding: utf-8 -*-
r"""
Step 45.  Make a page-image book searchable.

Some of the books in References are scans: the file is a stack of page
pictures with no text in it at all.  Golden's "Introduction to the History
of the Turkic Peoples" is 538 PNG images and about 4,000 characters of
real text, which is why step 44 could not search it.  This runs OCR over
the images and writes the text out.

    RUN-ocr-golden.bat            does Golden
    python step45_ocr_epub.py "path\to\some.epub"

It writes two things:

  References\<name>_OCR.txt          a plain text file you can open and
                                     search in Notepad.  Pages are marked
                                     "===PAGE n===".

  reports\_pagecache\<key>.txt       the same text in the place step 44
                                     looks for it, so searching the book
                                     works from then on with no change to
                                     any script.

OCR engine, in order of preference:
  1. tesseract, if it is on the PATH.  Better with diacritics.
  2. the OCR engine built into Windows 10 and 11, reached through
     PowerShell.  Nothing to install.

Neither is perfect on a 1911 typeface.  Treat the output as a finding aid:
good enough to locate a passage, not good enough to quote from.  Check the
printed page before citing anything.

Safe to stop and re-run.  Pages already done are skipped.
"""
import io, os, re, sys, glob, shutil, zipfile, subprocess

HERE  = os.path.dirname(os.path.abspath(__file__))
ROOT  = os.path.dirname(HERE)
REFS  = os.path.join(ROOT, "References")
WORK  = os.path.join(ROOT, "reports", "_ocr")
CACHE = os.path.join(ROOT, "reports", "_pagecache")

IMG_EXT = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")


def natural(s):
    return [int(x) if x.isdigit() else x.lower()
            for x in re.split(r"(\d+)", s)]


def pick_book(argv):
    if len(argv) > 1:
        p = argv[1]
        if os.path.exists(p):
            return p
        print("  not found: %s" % p)
        return None
    hits = [p for p in glob.glob(os.path.join(REFS, "*.epub"))
            if "golden" in os.path.basename(p).lower()]
    if hits:
        return hits[0]
    print("  no Golden epub in References, and no file given on the command line.")
    return None


def extract_images(book, dest):
    """Pull the page images out of an epub or a zip.  Returns a sorted list."""
    if not os.path.isdir(dest):
        os.makedirs(dest)
    have = [f for f in os.listdir(dest) if f.lower().endswith(IMG_EXT)]
    if have:
        print("  %d page images already extracted" % len(have))
        return sorted((os.path.join(dest, f) for f in have), key=natural)
    try:
        z = zipfile.ZipFile(book)
    except Exception as e:
        print("  cannot open as a zip/epub: %s" % e)
        return []
    names = [n for n in z.namelist() if n.lower().endswith(IMG_EXT)]
    names.sort(key=natural)
    out = []
    for i, n in enumerate(names):
        ext = os.path.splitext(n)[1].lower()
        d = os.path.join(dest, "p%04d%s" % (i + 1, ext))
        with open(d, "wb") as fh:
            fh.write(z.read(n))
        out.append(d)
    print("  extracted %d page images" % len(out))
    return out


PS1 = r'''
param([string]$Dir)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Foundation, ContentType=WindowsRuntime]
$null = [Windows.Storage.FileAccessMode, Windows.Foundation, ContentType=WindowsRuntime]

$m = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
  $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }
$asTaskGeneric = $m[0]

function Await($task, $type) {
  $asTask = $asTaskGeneric.MakeGenericMethod($type)
  $net = $asTask.Invoke($null, @($task))
  $net.Wait(-1) | Out-Null
  $net.Result
}

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if ($engine -eq $null) {
  $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage(
              (New-Object Windows.Globalization.Language "en-US"))
}
if ($engine -eq $null) { Write-Host "NO_OCR_ENGINE"; exit 2 }
Write-Host ("ENGINE " + $engine.RecognizerLanguage.LanguageTag)

$files = Get-ChildItem -Path $Dir -Include *.png,*.jpg,*.jpeg -Recurse:$false -File |
         Sort-Object Name
$i = 0
foreach ($f in $files) {
  $i++
  $out = [System.IO.Path]::ChangeExtension($f.FullName, ".txt")
  if (Test-Path $out) { continue }
  try {
    $sf     = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($f.FullName)) ([Windows.Storage.StorageFile])
    $stream = Await ($sf.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $dec    = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bmp    = Await ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
    $res    = Await ($engine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
    [System.IO.File]::WriteAllText($out, $res.Text, [System.Text.Encoding]::UTF8)
    $stream.Dispose()
  } catch {
    [System.IO.File]::WriteAllText($out, "", [System.Text.Encoding]::UTF8)
  }
  if ($i % 10 -eq 0) { Write-Host ("  ...{0} of {1}" -f $i, $files.Count) }
}
Write-Host "DONE"
'''


def ocr_tesseract(images):
    exe = shutil.which("tesseract")
    print("  using tesseract: %s" % exe)
    for i, img in enumerate(images):
        out = os.path.splitext(img)[0]
        if os.path.exists(out + ".txt"):
            continue
        try:
            subprocess.call([exe, img, out, "-l", "eng"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:
            io.open(out + ".txt", "w", encoding="utf-8").write(u"")
        if (i + 1) % 10 == 0:
            print("  ...%d of %d" % (i + 1, len(images)))
    return True


def ocr_windows(workdir):
    ps = os.path.join(workdir, "_ocr.ps1")
    io.open(ps, "w", encoding="utf-8").write(PS1)
    print("  using the OCR engine built into Windows")
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", ps, "-Dir", workdir]
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    except Exception as e:
        print("  could not start PowerShell: %s" % e)
        return False
    ok = True
    for raw in p.stdout:
        line = raw.decode("utf-8", "replace").rstrip()
        if line.startswith("NO_OCR_ENGINE"):
            print("  Windows has no OCR language pack installed.")
            ok = False
        elif line:
            print("  " + line if not line.startswith("  ") else line)
    p.wait()
    return ok


def assemble(images, book, stem):
    pages = []
    blank = 0
    for i, img in enumerate(images):
        t = os.path.splitext(img)[0] + ".txt"
        s = u""
        if os.path.exists(t):
            s = io.open(t, encoding="utf-8", errors="replace").read()
        if len(s.strip()) < 20:
            blank += 1
        pages.append((i + 1, s))

    body = u"".join(u"\n\x0c===PAGE %d===\n%s" % (n, s) for n, s in pages)

    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    key = re.sub(r"[^A-Za-z0-9]+", "_", os.path.basename(book))[:80] + ".txt"
    io.open(os.path.join(CACHE, key), "w", encoding="utf-8").write(body)

    readable = os.path.join(REFS, stem + "_OCR.txt")
    io.open(readable, "w", encoding="utf-8").write(
        body.replace(u"\x0c", u""))

    chars = sum(len(s) for _, s in pages)
    print("")
    print("  pages          : %d" % len(pages))
    print("  pages with text: %d" % (len(pages) - blank))
    print("  characters     : %d" % chars)
    print("")
    print("  readable copy  : References\\%s_OCR.txt" % stem)
    print("  search cache   : reports\\_pagecache\\%s" % key)
    return chars


def main():
    print("Step 45.  OCR a book that is only page images.")
    print("")
    book = pick_book(sys.argv)
    if not book:
        return 1
    stem = re.sub(r"[^A-Za-z0-9]+", "_",
                  os.path.splitext(os.path.basename(book))[0])[:48].strip("_")
    print("  book: %s" % os.path.basename(book))
    print("")

    workdir = os.path.join(WORK, stem)
    images = extract_images(book, workdir)
    if not images:
        print("  no page images found inside it. Nothing to OCR.")
        return 1

    todo = [i for i in images
            if not os.path.exists(os.path.splitext(i)[0] + ".txt")]
    print("  %d pages still to read" % len(todo))
    print("")

    if todo:
        if shutil.which("tesseract"):
            ocr_tesseract(images)
        elif not ocr_windows(workdir):
            print("")
            print("  No OCR engine is available.")
            print("  Either add an English language pack in")
            print("    Settings > Time and language > Language and region")
            print("  or install tesseract:")
            print("    winget install UB-Mannheim.TesseractOCR")
            print("  then run this again. Nothing is lost.")
            return 1

    chars = assemble(images, book, stem)
    print("")
    if chars < 20000:
        print("  That is very little text for a book. The OCR probably did")
        print("  not work properly. Paste this window to Claude.")
    else:
        print("  Now run RUN-search-togri.bat again. It will search this")
        print("  book along with the rest.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
