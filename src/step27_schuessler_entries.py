# -*- coding: utf-8 -*-
"""
step27_schuessler_entries.py -- reach Schuessler's entries through the OCR.

Step 25 found no Han characters; step 26 assumed a font problem. The sample
showed something else: the PDF carries an OCR text layer, the OCR did not
recognise Chinese at all, and it mangles the Latin diacritics badly. In the
sample, LHan lak prints as "!ilk", lok as "10k", and the eng of keng-c prints
as "kel)c". Searching for exact reconstructions is therefore hopeless.

Three things do survive the OCR, because they are plain ASCII:
  1. the tag "MHan", which marks every Han-period transcription Schuessler
     records. These are the most useful lines in the book for this project;
     the sample turned up  MHan 徑路 keng-c loc = qingiraq  by accident.
  2. the Mandarin column, ordinary toneless pinyin: dun, gu, shi, qi, dan.
  3. the Karlgren GSR numbers that head each entry block.

Output: reports\\readings\\schuessler_MHan.txt        every MHan line
        reports\\readings\\schuessler_py_<pinyin>.txt  entries by Mandarin
        reports\\readings\\schuessler_transcriptions.txt  MHan lines that also
                                                          look like a foreign word
"""
import io, os, re, sys, glob, collections, logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
OUT  = os.path.join(ROOT, "reports", "readings")
DIRS = [os.path.join(ROOT, d) for d in ("References", "new_refs", "my_resources")]

# character -> Mandarin readings to look for in the Mandarin column
PINYIN = {
    "頓": ["dun"], "谷": ["gu", "lu"], "閼": ["e", "yan"], "氏": ["shi"],
    "耆": ["qi"], "蠡": ["li"], "且": ["qie", "ju"], "累": ["lei"],
    "冒": ["mao", "mo"], "支": ["zhi"], "單": ["dan", "shan", "chan"],
    "鞮": ["di"], "若": ["ruo"], "徑": ["jing"], "路": ["lu"], "屠": ["tu"],
}

def book():
    for d in DIRS:
        if not os.path.isdir(d): continue
        for p in glob.glob(os.path.join(d, "**", "*.pdf"), recursive=True):
            if "minimal old chinese" in os.path.basename(p).lower():
                return p
    return None

def main():
    p = book()
    if not p: sys.exit("Schuessler PDF not found in References, new_refs or my_resources.")
    if not os.path.isdir(OUT): os.makedirs(OUT)
    import pdfplumber
    print("  %s" % os.path.basename(p)[:60])

    mhan = []
    bypy = collections.defaultdict(list)
    # a Mandarin syllable sits as its own token on an entry line
    pyre = {py: re.compile(r"(?<![a-z])" + py + r"(?![a-z])")
            for pys in PINYIN.values() for py in pys}

    with pdfplumber.open(p) as pdf:
        n = 0
        for pg in pdf.pages:
            n += 1
            if n % 50 == 0:
                sys.stdout.write("   page %d\r" % n); sys.stdout.flush()
            t = pg.extract_text() or ""
            if not t: continue
            lines = t.splitlines()
            for j, line in enumerate(lines):
                if "MHan" in line:
                    lo = max(0, j-2); hi = min(len(lines), j+2)
                    mhan.append((n, "\n".join(lines[lo:hi])))
                low = line.lower()
                for py, rx in pyre.items():
                    if rx.search(low) and len(bypy[py]) < 120:
                        lo = max(0, j-1); hi = min(len(lines), j+3)
                        bypy[py].append((n, "\n".join(lines[lo:hi])))
        print("   pages: %d" % n)

    with io.open(os.path.join(OUT, "schuessler_MHan.txt"), "w", encoding="utf8") as f:
        f.write("Every line tagged MHan in Schuessler 2009.\n"
                "These are the Han-period transcriptions he records.\n"
                "OCR note: l) is eng, 0 is often o, 1 and ! are often l.\n\n")
        for pno, blk in mhan:
            f.write("--- pdf page %d ---\n%s\n\n" % (pno, blk))
    print("   MHan lines: %d" % len(mhan))

    for py, hs in sorted(bypy.items()):
        if not hs: continue
        with io.open(os.path.join(OUT, "schuessler_py_%s.txt" % py), "w", encoding="utf8") as f:
            f.write("Schuessler 2009, lines with the Mandarin syllable '%s'.\n"
                    "Columns run: GSR, character (not OCRd), Mandarin, MC, LHan, OCM.\n\n" % py)
            for pno, blk in hs:
                f.write("--- pdf page %d ---\n%s\n\n" % (pno, blk))
    print("   pinyin files: %d" % sum(1 for h in bypy.values() if h))
    print()
    print("Read first:")
    print("  reports\\readings\\schuessler_MHan.txt   -- all Han transcriptions")
    print("  reports\\readings\\schuessler_py_dun.txt -- the entry for 頓")
    print()
    print("For 頓 the question is whether the entry shows one LHan value or two,")
    print("and whether 冒頓 appears in any MHan note.")

if __name__ == "__main__":
    main()
