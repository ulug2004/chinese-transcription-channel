# -*- coding: utf-8 -*-
"""
Step 40.  A ninth-century word list from the Irk Bitig (Tekin 1993).

Why this and not a third lexicon.  The Irk Bitig is one short manuscript,
sixty-five omens and a few hundred distinct words, against 6,820 headwords
in the Kāşgarî index and 2,110 in the Codex Cumanicus.  It is far too small
to run match rates against: the null model of §6.3 is built on lexicon
size.  What it is good for is dates.  It is ninth-century, three centuries
earlier than Kāşgarî, and it is the one Old Turkic text we hold that a
script can read.

POSITIVE FLAG ONLY.  A proposed reading whose word is in this list is
attested in Old Turkic by the ninth century.  A proposed reading whose word
is absent is NOT thereby unattested: four hundred words cannot show that
anything is missing from a language.  Reading absence as evidence is a
misuse of this file.

The glossary is OCR of a printed page and its diacritics are damaged, so
matching is done twice: an exact match on a folded form, and a looser match
on a consonant skeleton which will produce false friends.  Every match is
printed with its gloss so that a false friend is visible as one.  The run
of 4 September 2026 produced exactly that: the crude first version reported
a hit for tuğ, and the gloss showed it to be the verb tug- "to rise (of
sun)", not the noun.

Usage
    python step40_irk_bitig.py              read the PDF
    python step40_irk_bitig.py <raw.txt>    re-parse an existing raw dump
"""
import csv, os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
OUT  = os.path.join(ROOT, "reports")
DIRS = [os.path.join(ROOT, "new_refs"), os.path.join(ROOT, "References"),
        os.path.join(ROOT, "my_resources"),
        os.path.join(ROOT, "my_resources", "lexicons")]
NAME = re.compile(r"irk[ _-]?bitig|book of omens", re.I)
HEAD = re.compile(r"gl\s?ossary", re.I)
STOP = re.compile(r"bibl\s?iography", re.I)

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

def raw_pages(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    parts = re.split(r"--- pdf page (\d+) ---", txt)
    for i in range(1, len(parts) - 1, 2):
        yield int(parts[i]), parts[i + 1]

# --- OCR repair and folding ---------------------------------------------
OCR = [("l)", "ng"), ("I)", "ng"), ("�", "s"), ("ﬂ", "fl"),
       ("’", ""), ("'", ""), ("`", ""), ("·", "")]
FOLD = {"q": "k", "ñ": "ng", "ŋ": "ng", "ş": "s", "ı": "i", "ğ": "g",
        "ç": "c", "ā": "a", "ī": "i", "ū": "u", "ė": "e", "é": "e",
        "ï": "i", "ö": "o", "ü": "u", "ä": "a", "â": "a", "î": "i"}

def clean(w):
    w = (w or "").strip()
    for a, b in OCR:
        w = w.replace(a, b)
    # a parenthesised vowel that OCR read as I, l or 1 is really ı
    w = re.sub(r"\(([Il1])\)", "i", w)
    w = w.replace("(", "").replace(")", "")
    w = re.sub(r"\[[^\]]*\]", "", w)
    return w.strip(" ,;.")

def fold(w):
    w = clean(w).lower().rstrip("-")
    return "".join(FOLD.get(c, c) for c in w if c.isalpha())

VOW = set("aeiou")
def skeleton(w):
    """consonants only, so that damaged vowels cannot block a match"""
    return "".join(c for c in fold(w) if c not in VOW)

# --- glossary parsing ----------------------------------------------------
CITE = re.compile(r"^\s*(?:\(|[A-Za-zÀ-ÿ�]\s*[.!]|\d)")
NOISE = re.compile(r"gl\s?ossary|^\s*\d+\s*$|^\s*$", re.I)

def parse(pages):
    marked = [i for i, t in sorted(pages.items())
              if i > 5 and HEAD.search(t[:120]) and not STOP.search(t[:120])]
    if not marked:
        return [], (None, None)
    lo, hi = min(marked), max(marked)
    rows, seen = [], set()
    for i in range(lo, hi + 1):
        t = pages.get(i, "")
        if STOP.search(t):
            break
        for ln in t.split("\n"):
            ln = ln.rstrip()
            if not ln.strip() or NOISE.match(ln.strip()) or CITE.match(ln):
                continue
            toks = ln.split()
            if not toks:
                continue
            hw = toks[0]
            rest = toks[1:]
            if rest and rest[0] == "-":
                hw, rest = hw + "-", rest[1:]
            gl = " ".join(rest).strip()
            if len(clean(hw)) < 2 or not gl:
                continue
            k = fold(hw)
            if not k or k in seen:
                continue
            seen.add(k)
            rows.append({"headword": clean(hw), "gloss": re.sub(r"\s+", " ", gl),
                         "folded": k, "skeleton": skeleton(hw), "pdf_page": i})
    return rows, (lo, hi)

def _close(a, b):
    """same length, at most one differing character"""
    if len(a) != len(b):
        return False
    return sum(1 for x, y in zip(a, b) if x != y) <= 1

# words the project actually cares about, checked by direct search as well
TARGETS = ["kut", "tang", "tangri", "ulug", "kan", "tug", "bogu", "inak",
           "tin", "dogru", "togru", "korklug", "elti", "uchrug", "usrug"]

def main():
    lines = []
    def say(s=""):
        print(s); lines.append(s)

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        pages = dict(raw_pages(sys.argv[1]))
        say("Step 40.  re-parsing " + sys.argv[1])
    else:
        books = []
        for d in DIRS:
            if os.path.isdir(d):
                for p in sorted(glob.glob(os.path.join(d, "*.pdf"))):
                    if NAME.search(os.path.basename(p)):
                        books.append(p)
        if not books:
            print("No Irk Bitig PDF found. Looked in:")
            for d in DIRS:
                print("   " + d)
            return
        path = books[0]
        say("Step 40.  " + os.path.basename(path)[:74])
        pages = dict(pdf_pages(path))
        chars = sum(len(t) for t in pages.values())
        say("pages: %d   characters in the text layer: %d" % (len(pages), chars))
        if chars < 2000:
            say("No usable text layer; this is a scan without OCR.")
            return
        if not os.path.isdir(OUT):
            os.makedirs(OUT)
        with open(os.path.join(OUT, "irk_bitig_raw.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join("--- pdf page %d ---\n%s" % (i, pages[i])
                               for i in sorted(pages)))

    rows, (lo, hi) = parse(pages)
    say("glossary pages %s to %s; %d headwords parsed" % (lo, hi, len(rows)))
    say("")
    say("The glossary is set in two columns and the OCR interleaves them, so")
    say("the GLOSS column below is unreliable and the HEADWORD column is not.")
    say("Use this for which forms occur; read reports\\irk_bitig_raw.txt for")
    say("what any one of them means.")
    say("")
    say("first 30 entries, to show the parse is clean:")
    for r in rows[:30]:
        say("   %-16s %s" % (r["headword"], r["gloss"][:58]))

    # cross-check
    prop = os.path.join(DER, "author_proposals.csv")
    if os.path.exists(prop) and rows:
        with open(prop, encoding="utf-8-sig", newline="") as fh:
            props = list(csv.DictReader(fh))
        by_fold, by_skel = {}, {}
        for r in rows:
            by_fold.setdefault(r["folded"], r)
            by_skel.setdefault(r["skeleton"], r)
        say("")
        say("=" * 66)
        say("Which proposed readings use a word attested in the Irk Bitig")
        say("=" * 66)
        say("A hit dates the word to the ninth century. A miss means nothing.")
        say("Read the gloss: a verb glossed \"to ...\" is not a noun.")
        say("")
        n_exact = n_near = 0
        for p in props:
            name = (p.get("proposed_name") or "").strip()
            if not name or name.startswith("("):
                continue
            for w in re.split(r"[\s/]+", name):
                w = w.strip("-,;")
                if len(w) < 3:
                    continue
                f, s = fold(w), skeleton(w)
                if f in by_fold:
                    r = by_fold[f]; n_exact += 1
                    say("  exact  %-10s %-14s -> %-12s %s"
                        % (p["chinese"], w, r["headword"], r["gloss"][:44]))
                elif s and s in by_skel and _close(f, by_skel[s]["folded"]):
                    r = by_skel[s]; n_near += 1
                    say("  near   %-10s %-14s -> %-12s %s"
                        % (p["chinese"], w, r["headword"], r["gloss"][:44]))
        say("")
        say("%d exact, %d approximate. Check every gloss before using one."
            % (n_exact, n_near))

    if rows:
        say("")
        say("=" * 66)
        say("Direct check on the words this project argues about")
        say("=" * 66)
        by_fold2 = {}
        for r in rows:
            by_fold2.setdefault(r["folded"], []).append(r)
        for w in TARGETS:
            got = by_fold2.get(fold(w), [])
            if got:
                for r in got:
                    say("  %-9s IN   %-12s %s" % (w, r["headword"], r["gloss"][:50]))
            else:
                say("  %-9s not in the glossary (which proves nothing)" % w)

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    with open(os.path.join(OUT, "step40_summary.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    if rows:
        if not os.path.isdir(DER):
            os.makedirs(DER)
        p = os.path.join(DER, "irk_bitig_lexicon.csv")
        with open(p, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["headword", "gloss", "folded",
                                               "skeleton", "pdf_page"])
            w.writeheader(); w.writerows(rows)
        print("")
        print("written: " + p)
    print("written: " + os.path.join(OUT, "step40_summary.txt"))

if __name__ == "__main__":
    main()
