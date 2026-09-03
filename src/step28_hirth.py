# -*- coding: utf-8 -*-
"""
step28_hirth.py -- check the 徑路 comparison against Hirth 1908.

Section 9.1 of the paper credits the 徑路 = kıŋrak comparison to Hirth, The
Ancient History of China (1908), pp. 65-70, a citation carried over from the
literature and never checked against the book. Schuessler's own entry for 路
appears to give MHan 徑路 = qingiraq, so there are now two possible authorities
and the paper should cite whichever actually says it.

This searches the Hirth PDF for the comparison and for the rival Iranian
account, and writes the surrounding text. Nothing is uploaded.

Hirth writes in the romanisation of his day, so the script looks for several
spellings, and also dumps a window of raw pages around any hit so the passage
can be read in context.

Output: reports\\readings\\hirth_hits.txt
        reports\\readings\\hirth_pages_<a>_<b>.txt
"""
import io, os, re, sys, glob, logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
OUT  = os.path.join(ROOT, "reports", "readings")
DIRS = [os.path.join(ROOT, d) for d in ("References", "new_refs", "my_resources")]

# spellings Hirth or his contemporaries might use, plus the rival account
KEYS = [
    "kingrak", "king-rak", "kingirak", "qingiraq", "kinghrak", "kyngrak",
    "king-lu", "kinglu", "ching-lu", "chinglu", "king lu",
    "akinakes", "acinaces", "akinaka",
    "scythian sword", "sacred sword", "sword of", "oath",
    "hiung-nu", "hsiung-nu",
]
WINDOW = 2   # pages of context to dump around a hit

def find_pdf():
    for d in DIRS:
        if not os.path.isdir(d): continue
        for p in glob.glob(os.path.join(d, "**", "*.pdf"), recursive=True):
            b = os.path.basename(p).lower()
            if "hirth" in b or "ancient history of china" in b:
                return p
    return None

def main():
    p = find_pdf()
    if not p: sys.exit("Hirth PDF not found in References, new_refs or my_resources.")
    if not os.path.isdir(OUT): os.makedirs(OUT)
    import pdfplumber
    print("  %s" % os.path.basename(p)[:60])

    texts = {}
    hits = []
    with pdfplumber.open(p) as pdf:
        n = 0
        for pg in pdf.pages:
            n += 1
            if n % 50 == 0:
                sys.stdout.write("   page %d\r" % n); sys.stdout.flush()
            t = pg.extract_text() or ""
            texts[n] = t
            if not t: continue
            low = t.lower()
            for k in KEYS:
                if k in low:
                    for j, line in enumerate(t.splitlines()):
                        if k in line.lower():
                            hits.append((n, k, line.strip()))
        print("   pages: %d" % n)

    chars = sum(len(v) for v in texts.values())
    print("   text extracted: %d characters" % chars)
    if chars < 2000:
        print("   [!] almost no text layer; this PDF is a scan and needs OCR.")
        return

    with io.open(os.path.join(OUT, "hirth_hits.txt"), "w", encoding="utf8") as f:
        f.write("Hirth 1908, lines matching the search terms.\n"
                "Source: %s\n\n" % os.path.basename(p))
        for pno, k, line in hits:
            f.write("pdf p%-4d  [%s]  %s\n" % (pno, k, line))
    print("   matching lines: %d" % len(hits))

    pages = sorted({pn for pn, _, _ in hits})
    want = sorted({q for pn in pages for q in range(pn-WINDOW, pn+WINDOW+1) if q in texts})
    if want:
        a, b = want[0], want[-1]
        with io.open(os.path.join(OUT, "hirth_pages_%d_%d.txt" % (a, b)), "w", encoding="utf8") as f:
            for q in want:
                f.write("--- pdf page %d ---\n%s\n\n" % (q, texts[q]))
        print("   context written for %d pages (%d-%d)" % (len(want), a, b))
    else:
        print("   no hits. The book's own pages 65-70 are dumped instead;")
        with io.open(os.path.join(OUT, "hirth_pages_raw.txt"), "w", encoding="utf8") as f:
            for q in range(60, 100):
                if q in texts: f.write("--- pdf page %d ---\n%s\n\n" % (q, texts[q]))
        print("   see reports\\readings\\hirth_pages_raw.txt")
    print()
    print("Open reports\\readings\\hirth_hits.txt first. What is wanted is whether")
    print("Hirth actually makes the 徑路 = kingrak comparison, on which page, and")
    print("whether he mentions the Iranian akinakes account at all.")

if __name__ == "__main__":
    main()
