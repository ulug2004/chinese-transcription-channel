# -*- coding: utf-8 -*-
"""
Step 38.  What does Vovin 2003, Part 2, actually propose?

Part 1 declines to treat the titles at all and, on 孤塗, undercuts the
Yeniseian comparison rather than making it.  Part 2 is subtitled
"Vocabulary", so it is the place a positive Yeniseian form for any of our
items would be.  This script searches it for every Chinese form in the
record, for the characters those forms are made of, and for the terms
that would surround a proposal.

Output: reports\\readings\\vovin_part2_hits.txt
"""
import csv, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
OUT  = os.path.join(ROOT, "reports", "readings")
CAND = [os.path.join(ROOT, "References"), os.path.join(ROOT, "new_refs")]
NAME = re.compile(r"vovin.*(2003|part[_ ]?2|vocab)", re.I)

KEYWORDS = ["Proto-Yeniseian", "PY *", "Ket ", "Yug ", "Kott ", "Arin ",
            "Pumpokol", "Assan", "shan-yü", "shan-yu", "chan-yü",
            "Hsiung-nu", "Xiong-nu", "Xiongnu", "son'", '"son"',
            "heaven", "sky", "title", "loanword"]

def load_forms():
    p = os.path.join(DER, "author_proposals.csv")
    with open(p, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    forms = [r["chinese"].strip() for r in rows if r.get("chinese", "").strip()]
    chars = sorted({c for f in forms for c in f})
    return forms, chars

def pdf_pages(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader
    rd = PdfReader(path)
    for i, pg in enumerate(rd.pages, 1):
        try:
            yield i, pg.extract_text() or ""
        except Exception:
            yield i, ""

def main():
    forms, chars = load_forms()
    hits_files = []
    for d in CAND:
        if os.path.isdir(d):
            for p in sorted(glob.glob(os.path.join(d, "*.pdf"))):
                if NAME.search(os.path.basename(p)):
                    hits_files.append(p)
    if not hits_files:
        print("Vovin Part 2 not found. Looked for a PDF whose name matches")
        print("  vovin ... 2003 / part 2 / vocabulary   in:")
        for d in CAND:
            print("   " + d)
        return

    lines = []
    def say(s=""):
        print(s); lines.append(s)

    for path in hits_files:
        say("#" * 12 + " " + os.path.basename(path) + " " + "#" * 12)
        pages = list(pdf_pages(path))
        cjk = sum(len(re.findall(r"[㐀-鿿]", t)) for _, t in pages)
        say("pages: %d   Chinese characters in the text layer: %d" % (len(pages), cjk))
        if cjk == 0:
            say("  (no CJK in the text layer, so the character search will find nothing;")
            say("   the keyword search below still works)")
        say("")

        say("--- our items, by full form ---")
        for f in forms:
            where = [i for i, t in pages if f in t]
            if where:
                say("  %-6s pages %s" % (f, where))
        say("")
        say("--- our items, by single character ---")
        for c in chars:
            where = [i for i, t in pages if c in t]
            if where:
                say("  %s  pages %s" % (c, where[:12]))
        say("")
        say("--- keyword context ---")
        for kw in KEYWORDS:
            for i, t in pages:
                for m in re.finditer(re.escape(kw), t):
                    seg = re.sub(r"\s+", " ", t[max(0, m.start()-200):m.start()+260])
                    say("  [p%d] %s" % (i, seg))
                    break     # one example per page per keyword
        say("")

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    dest = os.path.join(OUT, "vovin_part2_hits.txt")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("")
    print("written: " + dest)

if __name__ == "__main__":
    main()
