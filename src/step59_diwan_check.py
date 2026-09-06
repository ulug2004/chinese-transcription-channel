# -*- coding: utf-8 -*-
r"""
Step 59.  Every Kāşgarî gloss in the supplement, checked against the Dīwān.

Until now every claim in the supplement attributed to Kāşgarî came from the
Türk Dil Kurumu index (the Dizin), which carries headwords and Turkish
glosses but no verses and no Arabic.  Dankoff and Kelly's edition of the
full text has since arrived and been OCR'd, so the glosses can be checked
against the work itself rather than against an index of it.

The two editions use different conventions, so the search is fuzzy:
Dankoff writes q for the back k, č for ç, š for ş, γ for ğ, and the OCR
mangles some of those further.  Each target is therefore turned into a
pattern that admits the plausible renderings, and every hit is printed with
its context so a reader can judge the match rather than trust a count.

A miss here is NOT a refutation.  The OCR is good but imperfect, Dankoff's
headword may be spelled differently from the TDK index's, and the Dīwān is
1,161 pages.  A miss means "look at the page", not "the gloss is wrong".

Output: reports\step59_diwan_check.txt
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
REP  = os.path.join(ROOT, "reports")
REFS = os.environ.get("DIWAN_DIR") or os.path.join(ROOT, "new_refs")

# Turkish letter -> what Dankoff, or the OCR of Dankoff, may show
# The OCR renders Dankoff's characters inconsistently, and one omission here
# cost a false negative: ç appears as J in the transliteration column and as
# é in the romanisation, so a pattern without those two misses the word
# entirely. Every class below is deliberately generous.
EQ = {u"k": u"[kqKQ]", u"q": u"[kqKQ]", u"ç": u"[čcéJj]", u"c": u"[cčéJj]",
      u"ş": u"[šs83S]", u"ğ": u"[γğgy7]", u"g": u"[gγy]",
      u"ı": u"[ıi1lI]", u"i": u"[iıI1]", u"ö": u"[öo06S]", u"ü": u"[üuiU]",
      u"y": u"[yγ]", u"n": u"[nŋ]", u"a": u"[aä]", u"e": u"[eäa]",
      u"t": u"[tT]", u"r": u"[rR]", u"l": u"[lL]", u"s": u"[sS3]"}

TARGETS = [
    (u"呴犁湖",   u"kalık",  u"hava, gök, sema (air, sky, heaven)"),
    (u"呴犁湖",   u"kılık",  u"disposition, manner"),
    (u"烏珠留若鞮", u"çal",    u"alaca, kır (dappled, grey)"),
    (u"搜諧若鞮",  u"sarıg",  u"sarı (yellow)"),
    (u"搜諧若鞮",  u"çakır",  u"blue (azraq), of eyes"),
    (u"軍臣",     u"kön",    u"düzelmek, doğrulmak (to straighten)"),
    (u"軍臣",     u"könit",  u"doğrultmak"),
    (u"谷蠡",     u"körklüg",u"iyi, güzel ve gösterişli"),
    (u"骨都侯",    u"kut",    u"kut, uğur, devlet (heavenly favour)"),
    (u"狐鹿姑",    u"kur",    u"kuşak, kemer (belt, girdle)"),
    (u"當戶",     u"tamga",  u"seal of the ruler"),
    (u"虛閭權渠",  u"kalkan", u"shield"),
    (u"徑路",     u"kıngrak",u"a knife like a cleaver"),
    (u"稽粥",     u"kiçig",  u"small, younger"),
    (u"頭曼",     u"tuman",  u"smoke, fog, mist"),
    (u"復株累若鞮", u"büktel", u"orta boylu, yassı arkalı"),
    (u"羯",       u"kad",    u"kar fırtınası (blizzard)"),
    (u"胡祿",     u"okluk",  u"sadak (quiver)"),
    (u"冒頓",     u"tug",    u"drum and banner borne before the king"),
    (u"閼氏",     u"ece",    u"elder sister"),
]


def pattern(w):
    return u"".join(EQ.get(c, re.escape(c)) for c in w)


def main():
    parts = []
    for p in (1, 2, 3):
        f = os.path.join(REFS, "Kasgari_DankoffKelly_Diwan_part%d_OCR.txt" % p)
        if os.path.exists(f):
            parts.append(io.open(f, encoding="utf-8", errors="replace").read())
    if not parts:
        sys.exit("Dīwān OCR not found under %s" % REFS)
    T = u"\n".join(parts)

    lines = []
    def say(s=u""):
        try:
            print(s)
        except Exception:
            print(s.encode("ascii", "replace").decode("ascii"))
        lines.append(s)

    say(u"Step 59.  The supplement's Kāşgarî glosses, checked against Dankoff and Kelly.")
    say(u"Dīwān OCR: %d characters over 1,161 pages." % len(T))
    say(u"")
    say(u"   A miss is not a refutation. It means the page needs an eye on it.")
    say(u"")
    found = miss = 0
    for row, word, gloss in TARGETS:
        pat = re.compile(u"\\b" + pattern(word), re.I)
        hits = [m for m in pat.finditer(T)]
        say(u"=" * 74)
        say(u"%-10s %-9s  %s" % (row, word, gloss))
        say(u"    pattern %s : %d hit(s)" % (pat.pattern, len(hits)))
        if not hits:
            miss += 1
            say(u"    NOT FOUND by this pattern.")
            continue
        found += 1
        seen = []
        for m in hits:
            c = u" ".join(T[max(0, m.start() - 90):m.start() + 170].split())
            if any(c[:60] == s[:60] for s in seen):
                continue
            seen.append(c)
            say(u"      ... %s" % c)
            if len(seen) >= 3:
                break
        say(u"")
    say(u"=" * 74)
    say(u"targets located: %d   not located by pattern: %d" % (found, miss))

    if not os.path.isdir(REP):
        os.makedirs(REP)
    io.open(os.path.join(REP, "step59_diwan_check.txt"), "w",
            encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: reports/step59_diwan_check.txt")


if __name__ == "__main__":
    main()
