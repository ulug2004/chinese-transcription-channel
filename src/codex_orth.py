# -*- coding: utf-8 -*-
r"""
codex_orth.py -- read the Codex Cumanicus in its own orthography.

Kuun's 1880 edition writes Cuman in medieval Latin spelling, not in the
transcription the Türk Dil Kurumu uses for Kāşgarî.  A search that treats
a Codex headword as though it were written in the modern system will read
consonants that are not there.  This has cost this project three separate
false leads:

    jain, jol, jil     read as affricates; they are yay, yol, yıl
    can, cun, coun     read as affricates; they are kan, kün, kavun
    tengis, tongus     read as n + g; they are teñiz, toñuz

Each rule below was validated the same way, and the validation runs with
`python codex_orth.py`.  A rule is kept only if applying it to Codex
headwords produces matches with Kāşgarî headwords that did not exist
before.  The DLT is an independent witness in a different orthography, so
a rule that is merely plausible produces nothing and a rule that is right
produces a list of real word pairs.

    rule                    new DLT matches   examples
    ng  -> ñ                        6         tengri>teñri, tang>tañ, ong>oñ
    initial j -> y                  9         jay>yay, jaz>yaz, jana>yana
    c before a, o, u -> k           8         can>kan, cara>kara, coy>koy
    x -> ş                          6         tax>taş, yax>yaş, ux>uş
    v -> w   (control)              0         nothing, as it should

The control matters: a transformation invented for the purpose gains
nothing, which is the evidence that the other four are not chance.

A LIMITATION, stated because it can mislead.  The rules are applied
uniformly to every headword.  A genuine -ng- cluster in a loanword would
therefore be rewritten as a single velar nasal, and a genuine c before a
back vowel as k.  The validation shows the rules are right in the general
case; it does not show they are right in every case.  Where a reading
turns on a Codex form whose spelling these rules changed, the source tag
records the original (Cod<-tongus) so it can be checked in Kuun.

NOT applied, and why:
    gh -> ğ            0 new matches
    initial ch -> ç    1 new match, too thin to trust
    final -h dropped   5 new matches, but they look like OCR damage
                       (ulah, korh, bogh, buth) rather than orthography
"""
import re

RULES = [
    (u"ng -> ñ",              re.compile(u"ng"),        u"ñ"),
    (u"initial j -> y",       re.compile(u"^j"),        u"y"),
    (u"c before a/o/u -> k",  re.compile(u"c(?=[aou])"), u"k"),
    (u"x -> ş",               re.compile(u"x"),         u"ş"),
]


def normalize(w):
    """A Codex headword in the transcription the rest of the project uses."""
    if not w:
        return w
    out = w.lower()
    for _, pat, rep in RULES:
        out = pat.sub(rep, out)
    return out


def tag(original, normalized, base=u"Cod"):
    """Source tag that keeps the original spelling visible when it changed."""
    return base if normalized == original.lower() else u"%s←%s" % (base, original)


if __name__ == "__main__":
    import csv, io, os, sys
    HERE = os.path.dirname(os.path.abspath(__file__))
    DER = os.path.join(os.path.dirname(HERE), "data", "derived")

    def col(p, k):
        return [(r[k] or "").strip().lower()
                for r in csv.DictReader(io.open(p, encoding="utf-8-sig"))
                if (r[k] or "").strip()]

    dlt = set(col(os.path.join(DER, "dlt_lexicon.csv"), "headword"))
    cod = col(os.path.join(DER, "cuman_lexicon.csv"), "headword")
    print("DLT headwords %d, Codex headwords %d" % (len(dlt), len(cod)))
    print("Codex headwords already matching a DLT headword: %d"
          % sum(1 for w in cod if w in dlt))
    print("")
    tests = list(RULES) + [(u"v -> w  (control)", re.compile(u"v"), u"w")]
    for name, pat, rep in tests:
        gained = []
        for w in cod:
            if w in dlt:
                continue
            v = pat.sub(rep, w)
            if v != w and v in dlt:
                gained.append((w, v))
        print("%-24s new matches: %3d   %s"
              % (name, len(gained), ", ".join("%s>%s" % g for g in gained[:6])))
    print("")
    both = sum(1 for w in cod if normalize(w) in dlt)
    print("With all four rules applied together, Codex headwords matching")
    print("a DLT headword rise from %d to %d."
          % (sum(1 for w in cod if w in dlt), both))
