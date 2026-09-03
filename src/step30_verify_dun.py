# -*- coding: utf-8 -*-
"""
step30_verify_dun.py -- check Schuessler's assignment of the stop reading to
頓 in 冒頓 against the other two reference works.

Schuessler 2009 states, on pages 209 and 361 independently, that in the name
冒頓 the reading is Mo-du, Later Han mək-tuət. That decides §9.2 of the paper,
so it is worth a second authority before the section is rewritten.

Two books are searched, differently, because they behave differently:

  Baxter & Sagart 2014  -- its Chinese encodes, so 頓 is searched directly.
      Expect little: step 25 found no hits for 頓, which probably means the
      character is outside their coverage. They reconstruct Old Chinese and do
      not normally discuss Han transcriptions of foreign names.

  Pulleyblank 1991      -- its Chinese does NOT encode (OCR without CJK), so it
      is searched by Mandarin and by the name's romanisations. Pulleyblank
      wrote on the Xiongnu for decades, so this is the likelier of the two.

Also searched for in both: the name in every romanisation in use, and the
words that would surround a discussion of it.

Output: reports\\readings\\verify_dun_<book>.txt   and a console summary.
"""
import io, os, re, sys, glob, collections, logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
OUT  = os.path.join(ROOT, "reports", "readings")
DIRS = [os.path.join(ROOT, d) for d in ("References", "new_refs", "my_resources")]

BOOKS = [
    ("baxtersagart",  ["old chinese", "new reconstruction"], ["頓", "冒"]),
    ("pulleyblank91", ["lexicon of reconstructed"],          []),
]
# the name, in the romanisations the literature uses
NAME = ["mao-tun", "maotun", "mao-dun", "maodun", "mo-tun", "motun",
        "mo-du", "modu", "mao-t'un", "mo-tu", "bagatur", "baghatur",
        "baγatur", "batur"]
# context words that would sit near a discussion of it
CTX  = ["xiong-nu", "xiongnu", "hsiung-nu", "hiung-nu", "shan-yü", "shan-yu",
        "chanyu", "shanyu", "hun ", "huns"]
# the reading itself, in the notations these books use
READ = ["twən", "tuən", "twət", "tuət", "twonh", "twon", "tuons", "tûns", "tuns"]

def find(needles):
    for d in DIRS:
        if not os.path.isdir(d): continue
        for p in glob.glob(os.path.join(d, "**", "*.pdf"), recursive=True):
            if all(n in os.path.basename(p).lower() for n in needles): return p
    return None

def main():
    if not os.path.isdir(OUT): os.makedirs(OUT)
    import pdfplumber
    any_hit = False
    for label, needles, chars in BOOKS:
        p = find(needles)
        if not p:
            print("   not found: %s" % label); continue
        print()
        print("=" * 64)
        print("  %s" % os.path.basename(p)[:60])
        print("=" * 64)
        keys = [(c, "character") for c in chars] \
             + [(k, "name")    for k in NAME] \
             + [(k, "context") for k in CTX] \
             + [(k, "reading") for k in READ]
        hits = []
        n = 0
        with pdfplumber.open(p) as pdf:
            for pg in pdf.pages:
                n += 1
                if n % 50 == 0:
                    sys.stdout.write("   page %d\r" % n); sys.stdout.flush()
                t = pg.extract_text() or ""
                if not t: continue
                low = t.lower()
                lines = t.splitlines()
                for j, line in enumerate(lines):
                    ll = line.lower()
                    for k, kind in keys:
                        if k in (line if kind == "character" else ll):
                            lo = max(0, j-1); hi = min(len(lines), j+2)
                            hits.append((n, kind, k, "\n".join(lines[lo:hi])))
                            break
        print("   pages: %d   matching lines: %d" % (n, len(hits)))
        tally = collections.Counter(kind for _, kind, _, _ in hits)
        for kind in ("character", "name", "context", "reading"):
            print("     %-10s %d" % (kind, tally[kind]))
        if tally["name"]:
            any_hit = True
            print()
            print("   *** the name itself appears. These are the lines that matter: ***")
            for pno, kind, k, blk in hits:
                if kind == "name":
                    print("     p%-4d [%s]" % (pno, k))
                    for l in blk.splitlines(): print("        " + l[:110])
        with io.open(os.path.join(OUT, "verify_dun_%s.txt" % label), "w", encoding="utf8") as f:
            f.write("%s -- searched for 頓 in the name 冒頓\nSource: %s\n\n"
                    % (label, os.path.basename(p)))
            for pno, kind, k, blk in hits:
                f.write("--- p%d  [%s: %s] ---\n%s\n\n" % (pno, kind, k, blk))
    print()
    if not any_hit:
        print("Neither book names 冒頓 in searchable text. That is a null result, not")
        print("a contradiction: it leaves Schuessler's statement unopposed rather than")
        print("corroborated. Pulleyblank 1962, which would discuss it, is the scan")
        print("with no text layer.")
    print("Files: reports\\readings\\verify_dun_*.txt")

if __name__ == "__main__":
    main()
