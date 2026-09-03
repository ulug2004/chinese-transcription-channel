# -*- coding: utf-8 -*-
"""
Step 35.  Which source vowel does a Later Han central vowel write?

The name of the second Xiongnu ruler is written with two characters.  The
first, MAO, has the Later Han reading *mek (Schuessler, with a central
vowel).  Two Turkic sources have been proposed for it:

    bogu   (bögü)   'wise, sage'    -- front rounded vowel
    baga   (baga-)  as in bagatur   -- open vowel

The consonant steps are identical for the two (source b written with an
m-initial character, medial velar written as the coda, final vowel not
written), so the vowel is the only place where the corpus can separate
them.  This script asks what a Later Han central vowel actually writes.

Corpora
  A  nti_transcription_pairs.csv + LHantab.tsv
     Later Han, the paper's own period.  Sanskrit has an open vowel and
     no front rounded vowel, so this corpus can price the baga reading
     directly and the bogu reading only by analogy.
  B  Sanskrit vowels that Later Han does not have (vocalic r) -- the
     analogy: what happens to a source vowel with no Chinese counterpart.
  C  ligeti_turkic_chinese_pairs.csv
     Yuan and Ming, out of period, but the only corpus here whose source
     language has front rounded vowels.

Nothing in A is restricted to the align=="exact" subset for a length
question, so the circularity that step 31 ran into does not arise: we
pair the k-th character with the k-th source vowel and drop any pair
where those two counts disagree.
"""
import csv, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")

def rd(path, delim=","):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=delim))

# ---------------------------------------------------------------- readings
def later_han_vowels():
    """character -> list of vowels, first reading first."""
    out = collections.OrderedDict()
    for row in rd(os.path.join(EXT, "LHantab.tsv"), "\t"):
        zi = (row.get("zi") or "").strip()
        vw = (row.get("vow") or "").strip()
        if not zi or not vw:
            continue
        out.setdefault(zi, [])
        if vw not in out[zi]:
            out[zi].append(vw)
    return out

# Later Han vowel classes.  The distinction that matters is open front/back
# unrounded (a-class) against central/reduced (schwa-class).
A_CLASS = set("a ɑ æ".split())
CENTRAL = set("ə ɨ ɐ".split())
def lh_class(v):
    core = v.strip()
    base = core[0] if core else ""
    if base in A_CLASS: return "a"
    if base in CENTRAL: return "schwa"
    if base in set("iey"): return "front"
    if base in set("uoɔ"): return "round"
    return "other:" + base

# ---------------------------------------------------------------- Sanskrit
SKT_V = ["ai", "au", "ā", "ī", "ū", "ṝ", "ṛ", "ḷ", "a", "i", "u", "e", "o"]
def skt_vowels(word):
    w = word.lower()
    out, i = [], 0
    while i < len(w):
        for v in SKT_V:
            if w.startswith(v, i):
                out.append(v); i += len(v); break
        else:
            i += 1
    return out

def skt_class(v):
    if v in ("a", "ā"): return "a"
    if v in ("i", "ī", "e", "ai"): return "front"
    if v in ("u", "ū", "o", "au"): return "round"
    if v in ("ṛ", "ṝ", "ḷ"): return "vocalic-r"
    return "other"

# ------------------------------------------------------------------ part A
def part_a(lh):
    pairs = rd(os.path.join(DER, "nti_transcription_pairs.csv"))
    tally = collections.Counter()
    unseen = kept = dropped = 0
    for row in pairs:
        chars = [c for c in (row.get("trad") or "") if "㐀" <= c <= "鿿"]
        vows  = skt_vowels(row.get("skt") or "")
        if not chars or len(chars) != len(vows):
            dropped += 1
            continue
        kept += 1
        for ch, sv in zip(chars, vows):
            rs = lh.get(ch)
            if not rs:
                unseen += 1
                continue
            tally[(skt_class(sv), lh_class(rs[0]))] += 1
    return tally, kept, dropped, unseen

def show(tally, title, rows=None):
    print("\n" + title)
    src = rows or sorted({s for s, _ in tally})
    cols = sorted({c for _, c in tally})
    w = max(11, *(len(c) + 2 for c in cols))
    print("  " + "source".ljust(12) + "".join(c.rjust(w) for c in cols) + "total".rjust(9))
    for s in src:
        n = sum(v for (a, b), v in tally.items() if a == s)
        if not n:
            continue
        line = "  " + s.ljust(12)
        for c in cols:
            v = tally.get((s, c), 0)
            line += ("%d (%.0f%%)" % (v, 100.0 * v / n)).rjust(w)
        print(line + str(n).rjust(9))

# ------------------------------------------------------------------ part C
EFEO_V = ["ouen", "ouei", "eou", "ien", "iao", "iou", "ai", "ei", "ao", "eu",
          "ou", "an", "en", "in", "on", "un", "a", "e", "i", "o", "u"]
def efeo_nuclei(syl):
    s = syl.lower()
    for v in EFEO_V:
        if v in s:
            return v
    return ""
def efeo_class(v):
    if not v: return "other"
    if v.startswith("eu"): return "schwa/eu"
    if v[0] == "a" or v in ("an",): return "a"
    if v[0] == "e": return "schwa/e"
    if v[0] in "iy": return "front"
    if v[0] in "ou": return "round"
    return "other"

TRK_V = ["ö", "ü", "ï", "ı", "â", "ê", "î", "ô", "û", "a", "e", "i", "o", "u"]
def trk_vowels(word):
    w = word.lower()
    out, i = [], 0
    while i < len(w):
        for v in TRK_V:
            if w.startswith(v, i):
                out.append(v); i += len(v); break
        else:
            i += 1
    return out
def trk_class(v):
    if v in ("ö", "ü"): return "front rounded (ö ü)"
    if v in ("a", "â"): return "open (a)"
    if v in ("e", "ê"): return "e"
    if v in ("i", "î", "ï", "ı"): return "front unrounded"
    if v in ("o", "u", "ô", "û"): return "back rounded"
    return "other"

def part_c():
    rows = rd(os.path.join(DER, "ligeti_turkic_chinese_pairs.csv"))
    tally = collections.Counter()
    kept = dropped = 0
    for row in rows:
        if (row.get("suspect") or "").strip():
            continue
        syls = [s for s in re.split(r"[-\s]+", (row.get("efeo_chinese") or "").strip()) if s]
        vows = trk_vowels(row.get("turkic") or "")
        if not syls or len(syls) != len(vows):
            dropped += 1
            continue
        kept += 1
        for sy, tv in zip(syls, vows):
            tally[(trk_class(tv), efeo_class(efeo_nuclei(sy)))] += 1
    return tally, kept, dropped


# ------------------------------------------------------------------ part D
def part_d(tally_a, tally_c):
    """Price the two Later Han readings of the first character."""
    def rate(t, s, c):
        n = sum(v for (a, b), v in t.items() if a == s)
        return t.get((s, c), 0), n

    print("\nD.  The first character has two Later Han readings.")
    print("    row 1  *mek   central vowel")
    print("    row 2  *mou   rounded vowel   (the reading behind the")
    print("           received Mao-tun and the modern pinyin mao)")

    k, n = rate(tally_a, "round", "round")
    k2, n2 = rate(tally_a, "a", "round")
    print("\n  if the character is read with its rounded vowel (row 2):")
    print("    a source rounded vowel is written this way   %4d of %4d  %5.1f%%"
          % (k, n, 100.0 * k / n if n else 0))
    print("    a source open vowel is written this way      %4d of %4d  %5.1f%%"
          % (k2, n2, 100.0 * k2 / n2 if n2 else 0))
    print("    ratio in favour of a rounded source          %5.1f to 1"
          % ((k / float(n)) / (k2 / float(n2)) if n and n2 and k2 else 0))

    k, n = rate(tally_a, "a", "schwa")
    k2, n2 = rate(tally_a, "round", "schwa")
    print("\n  if the character is read with its central vowel (row 1):")
    print("    a source open vowel is written this way      %4d of %4d  %5.1f%%"
          % (k, n, 100.0 * k / n if n else 0))
    print("    a source rounded vowel is written this way   %4d of %4d  %5.1f%%"
          % (k2, n2, 100.0 * k2 / n2 if n2 else 0))
    print("    ratio in favour of an open source            %5.1f to 1"
          % ((k / float(n)) / (k2 / float(n2)) if n and n2 and k2 else 0))

    k, n = rate(tally_c, "front rounded (\u00f6 \u00fc)", "round")
    print("\n  out of period, the source vowel we cannot reach in Later Han:")
    print("    source o-umlaut or u-umlaut written with a rounded")
    print("    Chinese syllable                             %4d of %4d  %5.1f%%"
          % (k, n, 100.0 * k / n if n else 0))
    k, n = rate(tally_c, "front rounded (\u00f6 \u00fc)", "schwa/e")
    print("    written with a central Chinese syllable      %4d of %4d  %5.1f%%"
          % (k, n, 100.0 * k / n if n else 0))
    print("\n  Reading the two together: the vowel does not decide the name")
    print("  on its own, it decides which reading of the character each")
    print("  candidate needs.  bogu needs row 2, baga needs row 1, and the")
    print("  corpus prices row 2 for a rounded source far more strongly")
    print("  than it prices row 1 for an open one.")

# -------------------------------------------------------------------- main
def main():
    lh = later_han_vowels()
    print("Later Han table: %d characters" % len(lh))

    tally_a, kept, dropped, unseen = part_a(lh)
    tally = tally_a
    print("\nA.  Later Han, Sanskrit source (%d pairs used, %d dropped on a"
          " vowel-count mismatch, %d characters absent from the table)"
          % (kept, dropped, unseen))
    show(tally, "A1.  source vowel written by which Later Han vowel class",
         ["a", "front", "round", "vocalic-r"])

    n_a = sum(v for (s, c), v in tally.items() if s == "a")
    a_a = tally.get(("a", "a"), 0)
    a_s = tally.get(("a", "schwa"), 0)
    n_r = sum(v for (s, c), v in tally.items() if s == "vocalic-r")
    r_s = tally.get(("vocalic-r", "schwa"), 0)
    print("\n  cost for a source open vowel (the baga reading):")
    print("    written with an a-class vowel      %4d of %4d  %5.1f%%"
          % (a_a, n_a, 100.0 * a_a / n_a if n_a else 0))
    print("    written with a central vowel       %4d of %4d  %5.1f%%"
          % (a_s, n_a, 100.0 * a_s / n_a if n_a else 0))
    if n_r:
        print("  a source vowel Later Han does not have (vocalic r):")
        print("    written with a central vowel       %4d of %4d  %5.1f%%"
              % (r_s, n_r, 100.0 * r_s / n_r if n_r else 0))

    tally_c, kept, dropped = part_c()
    tally = tally_c
    print("\nC.  Yuan and Ming, Turkic source, out of period"
          " (%d pairs used, %d dropped)" % (kept, dropped))
    show(tally, "C1.  source vowel written by which EFEO vowel class",
         ["front rounded (ö ü)", "open (a)", "e", "front unrounded",
          "back rounded"])
    n_o = sum(v for (s, c), v in tally.items() if s == "front rounded (ö ü)")
    o_a = tally.get(("front rounded (ö ü)", "a"), 0)
    n_op = sum(v for (s, c), v in tally.items() if s == "open (a)")
    o_op = tally.get(("open (a)", "a"), 0)
    print("\n  source ö or ü written with an a-vowel syllable  %4d of %4d  %5.1f%%"
          % (o_a, n_o, 100.0 * o_a / n_o if n_o else 0))
    print("  source a  written with an a-vowel syllable       %4d of %4d  %5.1f%%"
          % (o_op, n_op, 100.0 * o_op / n_op if n_op else 0))

    part_d(tally_a, tally_c)

if __name__ == "__main__":
    main()
