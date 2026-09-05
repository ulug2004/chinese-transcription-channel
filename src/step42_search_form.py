# -*- coding: utf-8 -*-
"""
Step 42.  Search every Turkic source on this machine for a proposed form.

    python step42_search_form.py                 searches canvus (the default)
    python step42_search_form.py cavus
    python step42_search_form.py "bogu tug"

Why it is not a plain text search.  The same word is spelled a dozen ways
across these sources: c/ch/ç/č, s/sh/ş/š, g/gh/ğ, i/ı, n/ñ/ŋ, and b/v/w
interchange between periods and editors, and the PDFs are OCR, so the
diacritics are damaged anyway.  So the script matches on a folded form,
where those sets are collapsed, and then again on a consonant skeleton
which ignores vowels entirely.  Skeleton hits are noisy by design; read
them, do not count them.

It searches, in this order:
    data\\derived\\*_lexicon.csv          the machine-readable lexicons
    my_resources\\lexicons\\*.epub        Clauson EDPT, Abu Hayyan, Kutadgu Bilig
    my_resources, References, new_refs   every PDF with a text layer

Extracted text is cached in reports\\_textcache so a second search is fast.

Output: reports\\readings\\search_<form>.txt
"""
import csv, io, os, re, sys, glob, zipfile, warnings
warnings.filterwarnings("ignore")

HERE  = os.path.dirname(os.path.abspath(__file__))
ROOT  = os.path.dirname(HERE)
DER   = os.path.join(ROOT, "data", "derived")
OUT   = os.path.join(ROOT, "reports", "readings")
CACHE = os.path.join(ROOT, "reports", "_textcache")
DIRS  = [os.path.join(ROOT, "my_resources", "lexicons"),
         os.path.join(ROOT, "my_resources"),
         os.path.join(ROOT, "References"),
         os.path.join(ROOT, "new_refs")]

FOLD = {"ç": "c", "č": "c", "ş": "s", "š": "s", "ž": "j", "ğ": "g", "ġ": "g",
        "ı": "i", "ï": "i", "î": "i", "ñ": "n", "ŋ": "n", "ń": "n",
        "ā": "a", "â": "a", "ä": "a", "ē": "e", "ê": "e", "ī": "i",
        "ō": "o", "ô": "o", "ö": "o", "ū": "u", "û": "u", "ü": "u",
        "b": "B", "v": "B", "w": "B", "p": "B",
        "’": "", "'": "", ":": "", "-": "", "ʔ": "", "`": ""}
VOW = set("aeiou")

def fold(t):
    t = t.lower()
    out = []
    for ch in t:
        if ch in FOLD:
            out.append(FOLD[ch])
        elif ch.isalpha() or ch.isspace():
            out.append(ch)
        else:
            out.append(" ")
    return "".join(out)

def skel(t):
    return "".join(c for c in fold(t) if c.isalpha() and c.lower() not in VOW)

# ---------------------------------------------------------------- sources
def epub_text(path):
    try:
        z = zipfile.ZipFile(path)
    except Exception:
        return ""
    parts = []
    for n in z.namelist():
        if n.lower().endswith((".xhtml", ".html", ".htm")):
            try:
                s = z.read(n).decode("utf-8", "replace")
            except Exception:
                continue
            s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
            s = re.sub(r"<[^>]+>", " ", s)
            parts.append(s)
    return "\n".join(parts)

def pdf_text(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            return ""
    try:
        rd = PdfReader(path)
    except Exception:
        return ""
    parts = []
    for pg in rd.pages:
        try:
            parts.append(pg.extract_text() or "")
        except Exception:
            pass
    return "\n".join(parts)

def cached(path):
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    key = re.sub(r"[^A-Za-z0-9]+", "_", os.path.basename(path))[:80] + ".txt"
    dest = os.path.join(CACHE, key)
    if os.path.exists(dest) and os.path.getmtime(dest) >= os.path.getmtime(path):
        return io.open(dest, encoding="utf-8", errors="replace").read()
    t = epub_text(path) if path.lower().endswith(".epub") else pdf_text(path)
    io.open(dest, "w", encoding="utf-8").write(t)
    return t

def main():
    q = " ".join(sys.argv[1:]).strip() or "çanvuş"
    fq, sq = fold(q).strip(), skel(q)
    lines = []
    def say(s=""):
        print(s); lines.append(s)

    say("Step 42.  Searching for: %s" % q)
    say("   folded form   : %s   (c=ç=č, s=ş=š, B=b=v=w=p, vowels bare)" % fq)
    say("   skeleton      : %s   (consonants only)" % sq)
    say("")

    # 1. the lexicons
    say("=" * 68)
    say("LEXICONS")
    say("=" * 68)
    for p in sorted(glob.glob(os.path.join(DER, "*lexicon*.csv"))):
        rows = list(csv.DictReader(io.open(p, encoding="utf-8-sig")))
        name = os.path.basename(p)
        hits_f = [r for r in rows if fq in fold(list(r.values())[0])]
        hits_s = [r for r in rows if sq and sq == skel(list(r.values())[0])]
        say("  %-28s %d headwords" % (name, len(rows)))
        for r in (hits_f or [])[:8]:
            say("      folded match : %s" % " | ".join(str(v)[:44] for v in list(r.values())[:2]))
        for r in (hits_s or [])[:8]:
            say("      skeleton     : %s" % " | ".join(str(v)[:44] for v in list(r.values())[:2]))
        if not hits_f and not hits_s:
            say("      no match")
    say("")

    # 2. the books
    say("=" * 68)
    say("BOOKS  (first run extracts and caches; later runs are fast)")
    say("=" * 68)
    seen = set()
    for d in DIRS:
        if not os.path.isdir(d):
            continue
        for p in sorted(glob.glob(os.path.join(d, "*.epub")) +
                        glob.glob(os.path.join(d, "*.pdf"))):
            rp = os.path.realpath(p)
            if rp in seen:
                continue
            seen.add(rp)
            t = cached(p)
            if len(t) < 2000:
                say("  %-52s no text layer" % os.path.basename(p)[:52])
                continue
            n_f = n_s = 0
            say("  %-52s %d chars" % (os.path.basename(p)[:52], len(t)))
            for ln in t.split("\n"):
                if not ln.strip():
                    continue
                fl = fold(ln)
                if fq in fl:
                    n_f += 1
                    if n_f <= 6:
                        say("      FOLDED  %s" % re.sub(r"\s+", " ", ln.strip())[:150])
            if n_f == 0 and sq:
                for ln in t.split("\n"):
                    for w in re.findall(r"[^\s]{2,24}", ln):
                        if skel(w) == sq:
                            n_s += 1
                            if n_s <= 6:
                                say("      SKELETON %-14s in: %s"
                                    % (w, re.sub(r"\s+", " ", ln.strip())[:110]))
                            break
            if n_f:
                say("      -> %d folded matches" % n_f)
            elif n_s:
                say("      -> 0 folded, %d skeleton matches (noisy, read them)" % n_s)
            else:
                say("      -> nothing")
    say("")
    say("A folded match is real. A skeleton match ignores vowels and will")
    say("catch unrelated words; it is there so that a damaged OCR vowel")
    say("cannot hide a genuine attestation.")

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    tag = re.sub(r"[^A-Za-z0-9]+", "_", q)[:40]
    dest = os.path.join(OUT, "search_%s.txt" % tag)
    io.open(dest, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("")
    print("written: " + dest)

if __name__ == "__main__":
    main()
