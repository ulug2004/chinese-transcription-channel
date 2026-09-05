# -*- coding: utf-8 -*-
"""
Step 39.  How many Later Han readings does 閼 have?

The open question on 閼氏 (docs\\open_question_yanzhi.md) is this.
Schuessler's LHantab gives 閼 exactly one value, ʔɑt, with a written -t.
But the compound is conventionally read yanzhi, and the parallel spelling
焉支 has 焉 = ʔɨan, with -n.  If 閼 also has a yan reading, the written -t
does not exist and the objection to the current entry disappears.

The table cannot answer it; a dictionary can.  This script looks the four
characters up in every reference PDF on this machine that has a usable
text layer, by character where the layer carries Chinese and by pinyin
where it does not (the Schuessler scan is OCR without CJK recognition,
which is what step 25 discovered).

Output: reports\\readings\\yanzhi_readings.txt
"""
import os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT  = os.path.join(ROOT, "reports", "readings")
DIRS = [os.path.join(ROOT, "new_refs"), os.path.join(ROOT, "References"),
        os.path.join(ROOT, "my_resources")]

# character -> the pinyin spellings a dictionary might use for it
TARGETS = {
    "閼": ["yan", "e", "yu", "ye", "at", "an"],
    "氏": ["shi", "zhi", "jing"],
    "焉": ["yan"],
    "支": ["zhi"],
}
# only these books are worth opening for this question
WANT = re.compile(r"schuessler|minimal old chinese|baxter|sagart|pulleyblank|"
                  r"lexicon of reconstructed", re.I)

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
    books = []
    for d in DIRS:
        if os.path.isdir(d):
            for p in sorted(glob.glob(os.path.join(d, "*.pdf"))):
                if WANT.search(os.path.basename(p)):
                    books.append(p)
    if not books:
        print("No Schuessler, Baxter-Sagart or Pulleyblank PDF found in:")
        for d in DIRS:
            print("   " + d)
        return

    lines = []
    def say(s=""):
        print(s); lines.append(s)

    for path in books:
        say("#" * 12 + " " + os.path.basename(path)[:70] + " " + "#" * 12)
        pages = list(pdf_pages(path))
        cjk = sum(len(re.findall(r"[㐀-鿿]", t)) for _, t in pages)
        say("pages: %d   Chinese characters in the text layer: %d" % (len(pages), cjk))

        if cjk:
            for ch in TARGETS:
                where = [i for i, t in pages if ch in t]
                say("  %s : %d pages  %s" % (ch, len(where), where[:20]))
                for i in where[:6]:
                    t = dict(pages)[i]
                    for m in list(re.finditer(re.escape(ch), t))[:2]:
                        seg = re.sub(r"\s+", " ", t[max(0, m.start()-170):m.start()+220])
                        say("     [p%d] %s" % (i, seg))
        else:
            say("  no CJK in the layer; searching by pinyin instead")
            for ch, pys in TARGETS.items():
                say("  --- %s, as %s ---" % (ch, "/".join(pys)))
                for py in pys:
                    pat = re.compile(r"(?<![A-Za-z])%s(?![A-Za-z])" % py, re.I)
                    shown = 0
                    for i, t in pages:
                        if "MHan" not in t and "LHan" not in t:
                            continue
                        for m in pat.finditer(t):
                            seg = re.sub(r"\s+", " ", t[max(0, m.start()-140):m.start()+200])
                            say("     [p%d %s] %s" % (i, py, seg))
                            shown += 1
                            break
                        if shown >= 4:
                            break
        say("")

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    dest = os.path.join(OUT, "yanzhi_readings.txt")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("")
    print("written: " + dest)

if __name__ == "__main__":
    main()
