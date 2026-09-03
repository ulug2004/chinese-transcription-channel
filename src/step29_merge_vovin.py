# -*- coding: utf-8 -*-
"""
step29_merge_vovin.py -- assemble the 18 single-page JSTOR captures of
Vovin (2000), "Did the Xiong-nu Speak a Yeniseian Language?", into one
ordered PDF, report whether they carry a text layer, and if they do, pull
out the passages this project needs.

Vovin 2000 is cited in the paper for the Yeniseian readings of 孤塗 and
單于. 孤塗 is also one of the two supplement rows still without a reading,
so what Vovin actually says about it matters twice.

Input : new_refs\\VOVIN_PART1\\p*_*.pdf   (one page each, from JSTOR)
Output: References\\Vovin_2000_Xiongnu_Yeniseian_Part1.pdf
        reports\\readings\\vovin_part1_hits.txt   (only if there is text)
"""
import io, os, re, sys, glob, hashlib, collections, logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
SRC  = os.path.join(ROOT, "new_refs", "VOVIN_PART1")
DST  = os.path.join(ROOT, "References", "Vovin_2000_Xiongnu_Yeniseian_Part1.pdf")
OUT  = os.path.join(ROOT, "reports", "readings")

KEYS = ["孤塗", "單于", "徑路", "qalek", "qal", "Ket ", "Kettic", "son'", '"son"',
        "chanyu", "shan-y", "sanoy", "Arin", "Pumpokol", "Kott",
        "titles", "loanword", "Turkic", "Hsiung-nu", "Xiong-nu"]

def pageno(p):
    m = re.search(r"[\\/]p(\d+)_", p)
    return int(m.group(1)) if m else 10**6

def main():
    if not os.path.isdir(SRC): sys.exit("Not found: %s" % SRC)
    files = sorted(glob.glob(os.path.join(SRC, "p*_*.pdf")), key=pageno)
    if not files: sys.exit("No p*.pdf files in %s" % SRC)
    print("  pages found: %d" % len(files))
    nums = [pageno(f) for f in files]
    missing = [n for n in range(1, max(nums)+1) if n not in nums]
    if missing: print("  [!] page numbers missing from the set: %s" % missing)

    # duplicate detection, since two of the captures had identical sizes
    seen = {}
    for f in files:
        h = hashlib.md5(io.open(f, "rb").read()).hexdigest()
        if h in seen:
            print("  [!] %s is byte-identical to %s"
                  % (os.path.basename(f)[:14], os.path.basename(seen[h])[:14]))
        else:
            seen[h] = f

    # merge
    writer = None
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        try:
            from PyPDF2 import PdfReader, PdfWriter
        except ImportError:
            PdfReader = None
    if PdfReader is None:
        print("  [!] neither pypdf nor PyPDF2 is installed, so the pages were not merged.")
        print("      run:  pip install pypdf")
    else:
        writer = PdfWriter()
        for f in files:
            for pg in PdfReader(f).pages: writer.add_page(pg)
        if not os.path.isdir(os.path.dirname(DST)): os.makedirs(os.path.dirname(DST))
        with io.open(DST, "wb") as fh: writer.write(fh)
        print("  merged -> References\\%s" % os.path.basename(DST))

    # text layer?
    try:
        import pdfplumber
    except ImportError:
        print("  pdfplumber not installed; cannot check for a text layer.")
        return
    total = 0
    hits = []
    for f in files:
        with pdfplumber.open(f) as pdf:
            for pg in pdf.pages:
                t = pg.extract_text() or ""
                total += len(t)
                for ln in t.splitlines():
                    for k in KEYS:
                        if k in ln:
                            hits.append((pageno(f), k, ln.strip())); break
    print("  text extracted across all pages: %d characters" % total)
    if total < 1500:
        print()
        print("  [!] These are page images with no text layer, which is what JSTOR's")
        print("      read-online capture produces. Searching them is not possible")
        print("      without OCR. The merged PDF is still readable by eye.")
        print()
        print("  What is wanted from it, if you read it: what Vovin proposes for")
        print("  孤塗 (the Chinese gloss is 子 'son') and for 單于, and whether he")
        print("  gives a Yeniseian form with a source and a page.")
        return
    if not os.path.isdir(OUT): os.makedirs(OUT)
    with io.open(os.path.join(OUT, "vovin_part1_hits.txt"), "w", encoding="utf8") as fh:
        fh.write("Vovin 2000 Part 1, lines matching the search terms.\n\n")
        for pn, k, ln in hits:
            fh.write("p%-3d [%s]  %s\n" % (pn, k, ln))
    print("  matching lines: %d -> reports\\readings\\vovin_part1_hits.txt" % len(hits))

if __name__ == "__main__":
    main()
