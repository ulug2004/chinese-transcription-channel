# -*- coding: utf-8 -*-
"""
lookup_lexicons.py
==================
Search every lexicon in this project for a word, from one prompt.

Searches, in order:
  1. data/derived/dlt_lexicon.csv    Kasgarli Mahmud, Divanu Lugati't-Turk (1072-77)
  2. data/derived/cuman_lexicon.csv  Codex Cumanicus, Kuun 1880
  3. my_resources/lexicons/*.epub    Clauson EDPT, Kutadgu Bilig, and anything else there

Matching ignores diacritics and Turkish/Turcological letter variants, so
"inaq" finds "ınaq", "ınāq", "ınak", "inag" and so on. That matters: the
same word is spelled a dozen ways across these sources.

Usage
-----
    python lookup_lexicons.py            interactive; blank line quits
    python lookup_lexicons.py inaq       one-shot
"""
import csv, io, os, re, sys, glob, zipfile, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DER  = os.path.join(ROOT, "data", "derived")
LEX  = os.path.join(ROOT, "my_resources", "lexicons")

# ------------------------------------------------------------------ folding
PRE = {"ı":"i","İ":"i","ŋ":"n","ñ":"n","ẓ":"z","ḍ":"d","ṭ":"t","ṣ":"s","ḏ":"d",
       "ġ":"g","ǧ":"g","đ":"d","ø":"o","æ":"a","œ":"o","ʼ":"","’":"","'":"",
       "ʔ":"","ʕ":"","ʾ":"","ʿ":""}
def fold(s):
    s = "".join(PRE.get(c, c) for c in (s or "").lower())
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    # Turcological spellings vs Turkish ones: q/k are the same letter here,
    # and "ng" is how the velar nasal is written when n-with-tail is not.
    # Without these two, "inaq" misses "inak" and "tengri" misses "teñri".
    s = s.replace("q", "k").replace("ng", "n").replace("x", "h")
    return re.sub(r"(.)\1+", r"\1", s)

def show(label, hits, limit=14):
    print()
    print("=" * 72)
    print(" %s — %d hit%s" % (label, len(hits), "" if len(hits) == 1 else "s"))
    print("=" * 72)
    if not hits:
        print("   (nothing)")
        return
    for h in hits[:limit]:
        print("   " + h)
    if len(hits) > limit:
        print("   ... and %d more" % (len(hits) - limit))

# ------------------------------------------------------------------ CSVs
def search_csv(path, word_col, gloss_cols, q, suffix=False):
    if not os.path.exists(path):
        return None
    out = []
    with io.open(path, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            hw = (r.get(word_col) or "").strip()
            if not hw:
                continue
            f = fold(hw)
            if suffix:
                ok = f.endswith(q) and len(f) > len(q)
            else:
                ok = (q == f) or (len(q) >= 3 and q in f)
            if ok:
                gl = " | ".join((r.get(c) or "").strip() for c in gloss_cols if r.get(c))
                extra = r.get("codex_page") or r.get("pdf_page") or ""
                out.append("%-22s %s%s" % (hw, gl[:78], ("   [p.%s]" % extra) if extra else ""))
    return out

# ------------------------------------------------------------------ EPUBs
TAG = re.compile(r"<[^>]+>")
def epub_text(path):
    parts = []
    try:
        with zipfile.ZipFile(path) as z:
            names = [n for n in z.namelist()
                     if n.lower().endswith((".xhtml", ".html", ".htm"))]
            for n in sorted(names):
                t = z.read(n).decode("utf-8", "ignore")
                t = TAG.sub(" ", t)
                parts.append(t)
    except Exception as e:
        return None, str(e)
    txt = re.sub(r"\s+", " ", " ".join(parts))
    return txt, None

TOKSPLIT = re.compile(r"\S+")
STRIP = " \t\r\n.,;:!?()[]{}<>\"'«»‘’“”·—–-*/|"

def search_epub(path, q, context=11):
    """Match whole words, not raw offsets.

    An earlier version folded the entire text and kept a character-by-character
    position index. Because folding rewrites "ng" to "n" and collapses doubled
    letters, the folded string and the index drift apart, and the context printed
    came from the wrong place. Folding one token at a time cannot drift, and it
    also stops a match from spanning two words.
    """
    txt, err = epub_text(path)
    if txt is None:
        return ["[could not read: %s]" % err]
    toks = TOKSPLIT.findall(txt)
    exact, partial = [], []
    for i, t in enumerate(toks):
        f = fold(t.strip(STRIP))
        if not f:
            continue
        if f == q:
            bucket = exact
        elif len(q) >= 4 and q in f:
            bucket = partial
        else:
            continue
        seg = " ".join(toks[max(0, i - context): i + context + 1])
        bucket.append(re.sub(r"\s+", " ", seg).strip())
    def dedupe(seq):
        seen, keep = set(), []
        for x in seq:
            k = x[:60]
            if k in seen:
                continue
            seen.add(k); keep.append(x)
        return keep
    exact, partial = dedupe(exact), dedupe(partial)
    out = ["[exact] " + e for e in exact[:20]]
    if partial and len(out) < 20:
        out += ["[in a longer word] " + e for e in partial[:20 - len(out)]]
    return out

# ------------------------------------------------------------------ driver
def lookup(term):
    term = term.strip()
    suffix = term.startswith("-")
    q = fold(term.lstrip("-").strip())
    if not q:
        print("  (empty search)")
        return
    if suffix:
        print("\nheadwords ENDING in: %s   (folded: %s)" % (term.lstrip("-"), q))
    else:
        print("\nsearching for: %s   (folded: %s)" % (term, q))

    r = search_csv(os.path.join(DER, "dlt_lexicon.csv"), "headword",
                   ["gloss_tr"], q, suffix)
    if r is None:
        print("\n   [dlt_lexicon.csv not found — run RUN-old-turkic.bat first]")
    else:
        show("Divanu Lugati't-Turk (Kasgarli Mahmud, 1072-77)", r)

    r = search_csv(os.path.join(DER, "cuman_lexicon.csv"), "headword",
                   ["gloss_lat"], q, suffix)
    if r is None:
        print("\n   [cuman_lexicon.csv not found — run RUN-codex-cumanicus.bat first]")
    else:
        show("Codex Cumanicus (Kuun 1880)", r)

    if suffix:
        print("\n   (suffix search covers the two extracted lexicons only —")
        print("    the epubs have no headword column to anchor an ending to)")
        return
    epubs = sorted(glob.glob(os.path.join(LEX, "*.epub")))
    if not epubs:
        print("\n   [no .epub files in my_resources\\lexicons]")
    for e in epubs:
        show(os.path.basename(e), search_epub(e, q), limit=10)

if __name__ == "__main__":
    print()
    print("  Lexicon lookup — Kasgarli, Codex Cumanicus, and the epubs in")
    print("  my_resources\\lexicons (Clauson, Kutadgu Bilig).")
    print("  Diacritics and i/i, s/s, g/g, c/c, q/k are ignored when matching.")
    print("  Start the word with a dash — e.g.  -ti  — to list headwords ENDING in it.")
    if len(sys.argv) > 1:
        lookup(" ".join(sys.argv[1:]))
    else:
        while True:
            try:
                t = input("\n  word to look up (blank to quit) > ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not t:
                break
            lookup(t)
    print("\n  done.")
