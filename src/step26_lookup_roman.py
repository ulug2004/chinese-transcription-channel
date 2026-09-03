# -*- coding: utf-8 -*-
"""
step26_lookup_roman.py -- step 25 found that Schuessler's and Pulleyblank's PDFs
extract their Latin text but not their Chinese: 872,421 and 800,008 characters of
text, and not one Han character among them. The CJK font in those files carries no
ToUnicode map, so the characters are drawn but not encoded.

The entries can still be reached, because Schuessler's own notation is Latin. This
step searches for the Later Han syllables themselves, taken from LHantab.tsv, plus
the Mandarin readings, and writes the surrounding lines.

It also dumps a short sample of raw extracted text from each book, so the layout
can be inspected and the search tightened if these keys are too loose.

Output: reports\\readings\\roman_<book>_<character>.txt
        reports\\readings\\_sample_<book>.txt
        a console summary
"""
import io, os, re, sys, csv, glob, collections, logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
OUT  = os.path.join(ROOT, "reports", "readings")
DIRS = [os.path.join(ROOT, d) for d in ("References", "new_refs", "my_resources")]
LHT  = os.path.join(ROOT, "data", "external", "LHantab.tsv")

BOOKS = [
    ("schuessler",   ["minimal old chinese"]),
    ("pulleyblank91",["lexicon of reconstructed"]),
    ("baxtersagart", ["old chinese", "new reconstruction"]),
]

# the characters that matter, with their Mandarin readings (toneless)
PINYIN = {
    "頓": ["dun", "du"], "谷": ["gu", "lu", "yu"], "閼": ["e", "yan", "yu"],
    "氏": ["shi", "zhi"], "耆": ["qi", "shi"], "蠡": ["li"],
    "且": ["qie", "ju"], "累": ["lei"], "冒": ["mao", "mo"],
    "支": ["zhi"], "單": ["dan", "shan", "chan"], "鞮": ["di"],
}
SUP = "ᴬᴮᶜ"   # Schuessler's tone marks, stripped for matching

def lhan_keys():
    keys = collections.defaultdict(set)
    if not os.path.exists(LHT):
        print("   [!] LHantab.tsv not found; using Mandarin only")
        return keys
    with io.open(LHT, encoding="utf8", errors="ignore") as f:
        for x in csv.DictReader(f, delimiter="\t"):
            z = (x.get("zi") or "").strip()
            sy = (x.get("syl_bok") or "").strip()
            if z in PINYIN and sy:
                keys[z].add("".join(c for c in sy if c not in SUP))
    return keys

def find_books():
    out = []
    for label, needles in BOOKS:
        for d in DIRS:
            if not os.path.isdir(d): continue
            got = None
            for p in glob.glob(os.path.join(d, "**", "*.pdf"), recursive=True):
                if all(n in os.path.basename(p).lower() for n in needles):
                    got = p; break
            if got: out.append((label, got)); break
    return out

def pages_of(path):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        for i, pg in enumerate(pdf.pages, 1):
            yield i, (pg.extract_text() or "")

def main():
    if not os.path.isdir(OUT): os.makedirs(OUT)
    LH = lhan_keys()
    books = find_books()
    if not books: sys.exit("No reference PDFs found.")

    for label, path in books:
        print()
        print("=" * 64)
        print("  %s" % os.path.basename(path)[:60])
        print("=" * 64)
        # search keys per character: the Later Han syllables, and pinyin
        keys = {}
        for ch, pys in PINYIN.items():
            k = set(LH.get(ch, set()))
            keys[ch] = k
        hits = collections.defaultdict(list)
        sample = []
        npages = 0
        for pno, text in pages_of(path):
            npages += 1
            if npages % 50 == 0:
                sys.stdout.write("   page %d\r" % npages); sys.stdout.flush()
            if not text: continue
            if 90 <= npages <= 92 and len(sample) < 60:
                sample.extend(("p%d| " % pno) + l for l in text.splitlines()[:20])
            low = text
            lines = low.splitlines()
            for j, line in enumerate(lines):
                for ch, ks in keys.items():
                    if len(hits[ch]) >= 40: continue
                    for k in ks:
                        if k and k in line:
                            lo = max(0, j-1); hi = min(len(lines), j+2)
                            hits[ch].append((pno, k, "\n".join(lines[lo:hi])))
                            break
        print("   pages: %d" % npages)
        with io.open(os.path.join(OUT, "_sample_%s.txt" % label), "w", encoding="utf8") as f:
            f.write("\n".join(sample))
        found = 0
        for ch, hs in hits.items():
            if not hs: continue
            found += 1
            with io.open(os.path.join(OUT, "roman_%s_%s.txt" % (label, ch)), "w", encoding="utf8") as f:
                f.write("%s -- lines containing a Later Han syllable of %s\n"
                        "Source: %s\nKeys: %s\n\n"
                        % (label, ch, os.path.basename(path), ", ".join(sorted(keys[ch]))))
                for pno, k, blk in hs:
                    f.write("--- pdf page %d  (matched %s) ---\n%s\n\n" % (pno, k, blk))
        print("   characters with at least one hit: %d of %d" % (found, len(PINYIN)))
        print("   " + "  ".join("%s:%d" % (c, len(hits[c])) for c in PINYIN))

    print()
    print("Wrote reports\\readings\\roman_*.txt and _sample_*.txt")
    print()
    print("Open reports\\readings\\_sample_schuessler.txt and paste the first")
    print("20 lines. That shows how the entries are laid out with the Chinese")
    print("missing, and lets the search be aimed properly.")

if __name__ == "__main__":
    main()
