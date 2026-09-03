# -*- coding: utf-8 -*-
"""
step25_lookup_readings.py -- pull the entries for the polyphonic characters out
of the reference books, so the reading printed in Appendix A can be checked
against the discussion rather than against the bare data table.

Step 24 found that 46 of the 107 characters in the record carry more than one
Later Han reading and that we print the first tabulated row in all 46. The data
release does not say which reading applies in which context; the books do.

Nothing is sent anywhere. Each book is searched locally and one report file per
character is written under reports\\readings\\ , so a large PDF never has to move.

Books searched (whichever are present):
    Schuessler 2009, Minimal Old Chinese and Later Han Chinese   <- the important one
    Baxter & Sagart 2014, Old Chinese: A New Reconstruction
    Pulleyblank 1991, Lexicon of Reconstructed Pronunciation
    Pulleyblank 1962, Consonantal System (Chinese translation)

Looked for in:  References\\ , new_refs\\ , my_resources\\

Output: reports\\readings\\<book>_<character>.txt   and a console summary.
"""
import io, os, re, sys, glob, collections, logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
OUT  = os.path.join(ROOT, "reports", "readings")
DIRS = [os.path.join(ROOT, d) for d in ("References", "new_refs", "my_resources")]

BOOKS = [
    ("schuessler",  ["minimal old chinese"]),
    ("baxtersagart",["old chinese", "new reconstruction"]),
    ("pulleyblank91",["lexicon of reconstructed"]),
    ("pulleyblank62",["consonantal system", "shang gu han yu"]),
]

# the characters step 24 flagged, most consequential first
TARGETS = ["頓", "谷", "閼", "氏", "耆", "蠡", "且", "累", "冒", "支", "單", "鞮",
           "曼", "稽", "臣", "呴", "犁", "衍", "呼", "邪", "復", "搜", "車", "而",
           "道", "連", "題", "當", "服", "胡"]
CONTEXT = 1          # lines of context kept either side of a hit
MAXHITS = 60         # per character per book

def find_books():
    found = []
    for label, needles in BOOKS:
        hit = None
        for d in DIRS:
            if not os.path.isdir(d): continue
            for p in glob.glob(os.path.join(d, "**", "*.pdf"), recursive=True):
                low = os.path.basename(p).lower()
                if all(n in low for n in needles):
                    hit = p; break
            if hit: break
        if hit: found.append((label, hit))
        else:   print("   not found: %s" % label)
    return found

def pages_of(path):
    """yield (page_number, text); try pdfplumber, then pypdf"""
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for i, pg in enumerate(pdf.pages, 1):
                yield i, (pg.extract_text() or "")
        return
    except ImportError:
        pass
    except Exception as e:
        print("   pdfplumber failed (%s), trying pypdf" % e)
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            sys.exit("Neither pdfplumber nor pypdf is installed.\n"
                     "  pip install pdfplumber")
    r = PdfReader(path)
    for i, pg in enumerate(r.pages, 1):
        yield i, (pg.extract_text() or "")

def main():
    if not os.path.isdir(OUT): os.makedirs(OUT)
    books = find_books()
    if not books: sys.exit("No reference PDFs found in References, new_refs or my_resources.")

    for label, path in books:
        print()
        print("=" * 64)
        print("  %s" % os.path.basename(path)[:60])
        print("=" * 64)
        hits = collections.defaultdict(list)
        chars = 0
        npages = 0
        for pno, text in pages_of(path):
            npages += 1
            if npages % 50 == 0:
                sys.stdout.write("   page %d\r" % npages); sys.stdout.flush()
            if not text: continue
            chars += len(text)
            lines = text.splitlines()
            for j, line in enumerate(lines):
                for t in TARGETS:
                    if t in line and len(hits[t]) < MAXHITS:
                        lo = max(0, j - CONTEXT); hi = min(len(lines), j + CONTEXT + 1)
                        hits[t].append((pno, "\n".join(lines[lo:hi])))
        print("   pages: %d   text extracted: %d characters" % (npages, chars))
        if chars < 2000:
            print("   [!] almost no text layer. This PDF is probably a scan and")
            print("       needs OCR before it can be searched.")
            continue
        found = 0
        for t in TARGETS:
            if not hits[t]: continue
            found += 1
            fn = os.path.join(OUT, "%s_%s.txt" % (label, t))
            with io.open(fn, "w", encoding="utf8") as f:
                f.write("%s -- entries mentioning %s\nSource: %s\n\n"
                        % (label, t, os.path.basename(path)))
                for pno, blk in hits[t]:
                    f.write("--- pdf page %d ---\n%s\n\n" % (pno, blk))
        print("   characters with at least one hit: %d of %d" % (found, len(TARGETS)))
        print("   %-6s %s" % ("", "  ".join("%s:%d" % (t, len(hits[t]))
                                            for t in TARGETS[:12])))
    print()
    print("Wrote per-character extracts to reports\\readings\\")
    print()
    print("Start with reports\\readings\\schuessler_頓.txt . The question is whether")
    print("Schuessler says which of tuen-C and tuet applies in a transcription, and")
    print("in particular whether he mentions 冒頓 . Paste the relevant lines only.")

if __name__ == "__main__":
    main()
