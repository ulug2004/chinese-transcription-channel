# -*- coding: utf-8 -*-
r"""
Step 44.  Who reads the Xiongnu title 屠耆 as *toγrï?

The paper says, in §9.1, "The Turkic-hypothesis literature reads it *toγrï",
and carries no citation for that.  This script goes looking for one in the
books on this machine, and prints every hit with its page number so that a
reference can be written from it.

It searches every PDF and EPUB in
    References\           the cited books, plus Doerfer and Pulleyblank
    my_resources\unused_reference\
    new_refs\
and looks for three kinds of thing:

  CHINESE   the characters themselves: 屠耆, 左右屠耆王, and the gloss 賢
  ROMANISED the character pair as western sinologists write it: T'u-ch'i,
            Tu-ch'i, tuqi, Tu-ki, Touki, and so on
  TURKIC    the proposed reading: toğrı, toğru, toghri, togri, toγrï,
            tuγrï, doğru ...

The Turkic forms are matched on a folded spelling (g=ğ=γ=gh, i=ı=ï, c=ç,
s=ş, and so on) because these books are OCR and the diacritics are damaged.

WHAT A USEFUL HIT LOOKS LIKE.  Not a bare mention of the title.  What is
wanted is a page where a Chinese or romanised form of 屠耆 and a Turkic
form stand near each other, because that is somebody proposing the
equation.  Those are printed first, under BOTH ON ONE PAGE, and they are
the ones to read.

Output: reports\readings\search_togri.txt
"""
import io, os, re, sys, glob, zipfile, warnings
warnings.filterwarnings("ignore")

HERE  = os.path.dirname(os.path.abspath(__file__))
ROOT  = os.path.dirname(HERE)
OUT   = os.path.join(ROOT, "reports", "readings")
CACHE = os.path.join(ROOT, "reports", "_pagecache")
DIRS  = [os.path.join(ROOT, "References"),
         os.path.join(ROOT, "my_resources", "unused_reference"),
         os.path.join(ROOT, "my_resources"),
         os.path.join(ROOT, "new_refs")]

# ---------------------------------------------------------------- folding
FOLD = {u"ç": u"c", u"č": u"c", u"ş": u"s", u"š": u"s", u"ž": u"j",
        u"ğ": u"g", u"ġ": u"g", u"γ": u"g", u"ɣ": u"g",
        u"ı": u"i", u"ï": u"i", u"î": u"i", u"í": u"i",
        u"ñ": u"n", u"ŋ": u"n", u"ń": u"n",
        u"ā": u"a", u"â": u"a", u"ä": u"a", u"à": u"a",
        u"ē": u"e", u"ê": u"e", u"ë": u"e",
        u"ī": u"i", u"ō": u"o", u"ô": u"o", u"ö": u"o",
        u"ū": u"u", u"û": u"u", u"ü": u"u",
        u"’": u"", u"‘": u"", u"'": u"", u"`": u"", u"ʼ": u"",
        u"ʻ": u"", u"ʼ": u"", u":": u"", u"-": u"", u"‐": u"",
        u"ʔ": u""}

def fold(t):
    t = t.lower()
    out = []
    for ch in t:
        if ch in FOLD:
            out.append(FOLD[ch])
        elif ch.isalpha() or ch.isdigit() or ch.isspace():
            out.append(ch)
        else:
            out.append(u" ")
    s = u"".join(out)
    # gh and kh are OCR/transliteration variants of the same velar
    s = s.replace(u"gh", u"g").replace(u"kh", u"k")
    return s

# what we are hunting for, in folded spelling
TURKIC = [u"togri", u"togru", u"togrï", u"togrul", u"togril", u"dogru",
          u"tugri", u"tugru", u"toqri", u"toqru"]
ROMAN  = [u"tuchi", u"tu chi", u"tuki", u"tu ki", u"touki", u"tuqi",
          u"tu qi", u"tuchï", u"tuki wang", u"tuqi wang"]
HAN    = [u"屠耆", u"左右屠耆王", u"屠耆王"]

# ---------------------------------------------------------------- readers
def epub_pages(path):
    try:
        z = zipfile.ZipFile(path)
    except Exception:
        return []
    pages = []
    for n in sorted(z.namelist()):
        if n.lower().endswith((".xhtml", ".html", ".htm")):
            try:
                s = z.read(n).decode("utf-8", "replace")
            except Exception:
                continue
            s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
            s = re.sub(r"<[^>]+>", " ", s)
            pages.append(s)
    return pages

def pdf_pages(path):
    PdfReader = None
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            return []
    try:
        rd = PdfReader(path)
    except Exception:
        return []
    pages = []
    for pg in rd.pages:
        try:
            pages.append(pg.extract_text() or "")
        except Exception:
            pages.append("")
    return pages

SEP = u"\n\x0c===PAGE %d===\n"

def cached_pages(path):
    """Return a list of page strings, cached to disk with page markers kept."""
    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    key = re.sub(r"[^A-Za-z0-9]+", "_", os.path.basename(path))[:80] + ".txt"
    dest = os.path.join(CACHE, key)
    if os.path.exists(dest) and os.path.getmtime(dest) >= os.path.getmtime(path):
        raw = io.open(dest, encoding="utf-8", errors="replace").read()
    else:
        pgs = epub_pages(path) if path.lower().endswith(".epub") else pdf_pages(path)
        raw = u"".join((SEP % (i + 1)) + p for i, p in enumerate(pgs))
        io.open(dest, "w", encoding="utf-8").write(raw)
    out = []
    for chunk in raw.split(u"\x0c"):
        m = re.match(r"===PAGE (\d+)===\n", chunk)
        if m:
            out.append((int(m.group(1)), chunk[m.end():]))
    return out

# ---------------------------------------------------------------- search
def find(page_text):
    """Return (han, roman, turkic) lists of the strings actually seen."""
    f = fold(page_text)
    han = [h for h in HAN if h in page_text]
    rom = [r for r in ROMAN if r in f]
    tur = sorted(set(fold(t) for t in TURKIC if fold(t) in f))
    return han, rom, tur

def snippet(text, needles, width=150):
    f = fold(text)
    for n in needles:
        k = text.find(n)
        if k < 0:
            k = f.find(fold(n))
        if k >= 0:
            a = max(0, k - width // 2)
            return re.sub(r"\s+", " ", text[a:a + width]).strip()
    return re.sub(r"\s+", " ", text[:width]).strip()

def main():
    lines = []
    def say(s=u""):
        try:
            print(s)
        except Exception:
            print(s.encode("ascii", "replace").decode("ascii"))
        lines.append(s)

    say(u"Step 44.  Looking for a source for the *togri reading of 屠耆.")
    say(u"")

    both, only_han, only_tur = [], [], []
    seen = set()
    files = 0
    for d in DIRS:
        if not os.path.isdir(d):
            continue
        for p in sorted(glob.glob(os.path.join(d, "*.pdf")) +
                        glob.glob(os.path.join(d, "*.epub"))):
            rp = os.path.realpath(p)
            if rp in seen:
                continue
            seen.add(rp)
            name = os.path.basename(p)
            pages = cached_pages(p)
            chars = sum(len(t) for _, t in pages)
            files += 1
            if chars < 2000:
                say(u"  %-56s no text layer, skipped" % name[:56])
                continue
            say(u"  %-56s %d pages" % (name[:56], len(pages)))
            for num, t in pages:
                han, rom, tur = find(t)
                if (han or rom) and tur:
                    both.append((name, num, han + rom, tur, snippet(t, tur)))
                elif han and not tur:
                    only_han.append((name, num, han, snippet(t, han)))
                elif tur and not (han or rom):
                    only_tur.append((name, num, tur, snippet(t, tur)))

    say(u"")
    say(u"=" * 70)
    say(u"BOTH ON ONE PAGE  -  read these first")
    say(u"=" * 70)
    if not both:
        say(u"  none.  No page in these books carries a form of 屠耆 and a")
        say(u"  Turkic *togri form together.  On this evidence the claim")
        say(u"  cannot be cited to anything held here.")
    for name, num, ch, tur, sn in both[:40]:
        say(u"")
        say(u"  %s  page %d" % (name, num))
        say(u"      Chinese/romanised : %s" % u", ".join(ch))
        say(u"      Turkic            : %s" % u", ".join(tur))
        say(u"      %s" % sn)

    say(u"")
    say(u"=" * 70)
    say(u"THE TITLE ALONE  (%d pages)" % len(only_han))
    say(u"=" * 70)
    for name, num, ch, sn in only_han[:40]:
        say(u"  %-40s p.%-5d %s" % (name[:40], num, sn[:100]))
    if len(only_han) > 40:
        say(u"  ... and %d more" % (len(only_han) - 40))

    say(u"")
    say(u"=" * 70)
    say(u"A TURKIC *togri FORM ALONE  (%d pages)" % len(only_tur))
    say(u"=" * 70)
    for name, num, tur, sn in only_tur[:40]:
        say(u"  %-40s p.%-5d %-14s %s" % (name[:40], num, u",".join(tur)[:14], sn[:80]))
    if len(only_tur) > 40:
        say(u"  ... and %d more" % (len(only_tur) - 40))

    say(u"")
    say(u"%d files searched." % files)
    say(u"Page numbers are positions in the PDF, not the printed page number.")
    say(u"Check the printed number on the page itself before citing it.")

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    dest = os.path.join(OUT, "search_togri.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)

if __name__ == "__main__":
    main()
