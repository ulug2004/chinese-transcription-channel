# -*- coding: utf-8 -*-
"""
Step 36.  Pull one numbered entry out of Doerfer, TMEN, across every volume
present on this machine.

    python step36_doerfer_entry.py 817
    RUN-doerfer-entry.bat 817

Entry 817 is the one Clauson cites at the end of his article on bagatur.
Entry 969 is tug.  The script does not care which: it scans all four
volumes, reports the entry range each volume covers, and prints the block
that follows the entry number in whichever volume contains it.  The
addenda in the later volumes repeat the number, so more than one volume
can answer.

Output goes to reports\\readings\\doerfer_entry_<n>.txt
"""
import os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT  = os.path.join(ROOT, "reports", "readings")
FOLDERS = ["new_refs", "References", "my_resources",
           os.path.join("my_resources", "lexicons"), "Downloads"]
PAT = re.compile(r"doerfer|eupersischen", re.I)

def pages(path):
    """yield (page_number, text) using whatever extractor is installed."""
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            PdfReader = None
    if PdfReader is not None:
        rd = PdfReader(path)
        for i, pg in enumerate(rd.pages, 1):
            try:
                yield i, pg.extract_text() or ""
            except Exception:
                yield i, ""
        return
    from pdfminer.high_level import extract_text
    txt = extract_text(path) or ""
    for i, chunk in enumerate(txt.split("\f"), 1):
        yield i, chunk

def entry_numbers(text):
    return [int(m.group(1)) for m in re.finditer(r"(?m)^\s*(\d{2,4})\s*\.", text)]

def main():
    want = sys.argv[1] if len(sys.argv) > 1 else "817"
    want = re.sub(r"\D", "", want) or "817"
    n = int(want)
    head = re.compile(r"(?m)^\s*%d\s*\." % n)

    found = []
    for folder in FOLDERS:
        d = os.path.join(ROOT, folder)
        if not os.path.isdir(d):
            continue
        for p in sorted(glob.glob(os.path.join(d, "*.pdf"))):
            if PAT.search(os.path.basename(p)):
                found.append(p)
    found = sorted(set(found))
    if not found:
        print("No Doerfer volume found. Looked in:")
        for f in FOLDERS:
            print("   " + os.path.join(ROOT, f))
        return

    lines = []
    def say(s=""):
        print(s)
        lines.append(s)

    say("Doerfer, entry %d.  %d volume(s) on disk." % (n, len(found)))
    for p in found:
        say("")
        say("#" * 12 + " " + os.path.basename(p) + " " + "#" * 12)
        nums, hits = [], []
        for pno, txt in pages(p):
            if not txt:
                continue
            nums += entry_numbers(txt)
            if head.search(txt):
                hits.append((pno, txt))
        if nums:
            say("   entry numbers seen: %d to %d" % (min(nums), max(nums)))
        else:
            say("   no entry numbers recognised (scan without a text layer?)")
        if not hits:
            say("   entry %d not in this volume" % n)
            continue
        for pno, txt in hits:
            m = head.search(txt)
            start = m.start()
            nxt = re.search(r"(?m)^\s*%d\s*\." % (n + 1), txt[start:])
            end = start + nxt.start() if nxt else min(len(txt), start + 4000)
            say("")
            say("--- pdf page %d ---" % pno)
            say(txt[start:end].rstrip())

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    dest = os.path.join(OUT, "doerfer_entry_%d.txt" % n)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("")
    print("written: " + dest)

if __name__ == "__main__":
    main()
