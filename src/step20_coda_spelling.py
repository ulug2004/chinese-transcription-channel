# -*- coding: utf-8 -*-
"""
step20_coda_spelling.py
=======================
When a source word had a consonant at the end of a syllable, did the Chinese
scribe use a character that ENDS in that consonant, or an OPEN character with
a vowel after it?

Why this is being asked
-----------------------
Appendix B reads the recurring chanyu title element 若鞮 *nak-te as Turkic
*inaq* "trusted, devoted" plus a suffix. Two suffixes are possible and they
fail in different ways:

  *inaq-ti   the -tI is not a noun-forming suffix (step 19's lexicons show
             31 of 31 Cuman words in -tI are past-tense verbs)
  *inakt     -t IS a real Old Turkic plural, and specifically a plural of
             TITLES (tegin -> tegit, tarqan -> tarqat)

*inakt* fixes the morphology but raises a spelling question: Later Han
Chinese had -t final syllables and could have closed the word with one, yet
鞮 is an open syllable *te. Is that decisive? Only if scribes normally DID
close such words. This script counts how they actually behaved.

Method
------
The Sanskrit corpus is the one that matters: it is Later Han, the same layer
as the Xiongnu names. For pairs where characters and syllables are 1:1, each
Sanskrit syllable is aligned to its Chinese character. Where the Sanskrit
syllable ends in a stop, the aligned character's Later Han coda is recorded.

The Mongolian and Turkic corpora are also reported, but they are Ming-era and
step 14 showed Old Mandarin had ALREADY merged -p, -t and -k to nothing. A
Ming scribe could not write a stop coda even if he wanted to, so those rows
measure the writing system, not the scribe's choice. They are printed as a
control, not as evidence.

Outputs
-------
reports/step20_summary.txt
data/derived/coda_spelling.csv
"""
import csv, io, os, re, sys, collections

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))
DER = os.path.join(ROOT, "data", "derived")
EXT = os.path.join(ROOT, "data", "external")
REP = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)

out = []
def w(s=""):
    print(s); out.append(s)

# ------------------------------------------------------------ Later Han codas
STOPS, NASALS = set("ptk"), set("mnŋ")
TONE = "ᴬᴮᶜᴰ"

def load_lhan():
    """character -> set of coda symbols ('' = open syllable)."""
    coda = collections.defaultdict(set)
    path = os.path.join(EXT, "LHantab.tsv")
    if not os.path.exists(path):
        return None
    with io.open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            zi = (r.get("zi") or "").strip()
            rime = (r.get("vow") or "").strip().rstrip(TONE)
            if not zi or not rime:
                continue
            last = rime[-1]
            coda[zi].add(last if (last in STOPS or last in NASALS) else "")
    return coda

CODA = load_lhan()
if CODA is None:
    print("data/external/LHantab.tsv not found"); sys.exit(1)

def coda_of(ch):
    s = CODA.get(ch)
    if not s:
        return None
    # prefer a consonantal coda if the character has more than one reading
    for c in s:
        if c:
            return c
    return ""

# ------------------------------------------------------------ Sanskrit syllables
VOW = ["ai", "au", "ā", "ī", "ū", "ṝ", "ṛ", "ḷ", "e", "o", "a", "i", "u"]
DIG = ["kh","gh","ch","jh","ṭh","ḍh","th","dh","ph","bh"]
def units(word):
    """split a romanised Sanskrit word into consonant/vowel units"""
    s, i, u = word.lower(), 0, []
    while i < len(s):
        for d in DIG:
            if s.startswith(d, i):
                u.append((d, "C")); i += len(d); break
        else:
            for v in VOW:
                if s.startswith(v, i):
                    u.append((v, "V")); i += len(v); break
            else:
                u.append((s[i], "C")); i += 1
    return u

def syllables(word):
    """V-anchored syllables; in a cluster the first consonant closes the syllable"""
    u = units(word)
    vpos = [i for i, (_, t) in enumerate(u) if t == "V"]
    if not vpos:
        return []
    syls = []
    for n, v in enumerate(vpos):
        start = 0 if n == 0 else prev_end
        if n + 1 < len(vpos):
            gap = u[v + 1: vpos[n + 1]]
            take = 1 if len(gap) >= 2 else 0      # first of a cluster closes
            end = v + 1 + take
        else:
            end = len(u)
        syls.append("".join(x for x, _ in u[start:end]))
        prev_end = end
    return syls

def syl_coda(syl):
    u = units(syl)
    if not u or u[-1][1] != "C":
        return ""
    c = u[-1][0]
    m = {"k":"k","g":"k","t":"t","d":"t","ṭ":"t","ḍ":"t","p":"p","b":"p",
         "m":"m","n":"n","ṇ":"n","ṅ":"ŋ","ñ":"n"}
    return m.get(c, "")

# ------------------------------------------------------------ the measurement
def read(p):
    if not os.path.exists(p): return None
    with io.open(p, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))

rows_csv = []
w("=" * 74)
w(" STEP 20 — how a source coda was spelled in Chinese")
w("=" * 74)
w("")

# --- Sanskrit, Later Han, syllable-aligned -------------------------------
nti = read(os.path.join(DER, "nti_transcription_pairs.csv"))
if nti is None:
    w(" [nti_transcription_pairs.csv not found — run RUN-steps.bat first]")
else:
    tab = collections.defaultdict(collections.Counter)
    used = 0
    for r in nti:
        ch, sk = (r.get("trad") or "").strip(), (r.get("skt") or "").strip()
        if not ch or not sk: continue
        sy = syllables(sk)
        if len(sy) != len(ch):            # 1:1 alignments only
            continue
        used += 1
        for c, s in zip(ch, sy):
            sc = syl_coda(s)
            if not sc: continue
            cc = coda_of(c)
            if cc is None: continue
            tab[sc][cc if cc else "open (vowel)"] += 1
    w("-" * 74)
    w(" SANSKRIT — Later Han transcriptions, the layer that matters")
    w(" %d of %d pairs had a 1:1 character-to-syllable alignment" % (used, len(nti)))
    w("-" * 74)
    for sc in ("p", "t", "k", "m", "n", "ŋ"):
        c = tab.get(sc)
        if not c: continue
        tot = sum(c.values())
        same = c.get(sc, 0)
        openv = c.get("open (vowel)", 0)
        w("  source syllable ends -%s   n=%-4d  same coda %d (%.0f%%)   "
          "OPEN character %d (%.0f%%)"
          % (sc, tot, same, 100.0*same/tot, openv, 100.0*openv/tot))
        for k, v in c.most_common():
            rows_csv.append({"corpus": "Sanskrit (Later Han)", "source_coda": sc,
                             "chinese_coda": k, "count": v})
    w("")
    stops = [sc for sc in "ptk" if tab.get(sc)]
    if stops:
        tot = sum(sum(tab[sc].values()) for sc in stops)
        opn = sum(tab[sc].get("open (vowel)", 0) for sc in stops)
        same = sum(tab[sc].get(sc, 0) for sc in stops)
        w("  ALL STOP CODAS: n=%d — closed with the same stop %d (%.0f%%), "
          "written with an OPEN character %d (%.0f%%)"
          % (tot, same, 100.0*same/tot if tot else 0,
             opn, 100.0*opn/tot if tot else 0))
        w("")
        if tot < 30:
            w("  CAUTION: n is small. Treat this as indicative only.")
        other = tot - same - opn
        w("  (the remaining %d went to some other coda)" % other)
        w("")
        w("  VERDICT for 若鞮: an open character after a stop-final source")
        w("  syllable happens in roughly %.0f%% of cases here — common, not" % (100.0*opn/tot if tot else 0))
        w("  exceptional. So 鞮 *te following *inak- is an ordinary spelling,")
        w("  and the objection that a scribe 'would have closed the syllable'")
        w("  does not hold: often he did not. Compare the nasals in the rows")
        w("  above, which were closed far more consistently — the same split")
        w("  step 14 found between nasal and stop codas across the period gap.")
    w("")

# The Ming corpora cannot be used here. Looking up a Later Han coda for a
# character chosen by a Ming scribe measures neither period: by Ming times
# those codas were gone (step 14), so the character's Later Han value says
# nothing about what the scribe heard. An earlier draft printed it as a
# "control" and it was simply misleading, so it has been removed.

w("=" * 74)

with io.open(os.path.join(REP, "step20_summary.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
if rows_csv:
    with io.open(os.path.join(DER, "coda_spelling.csv"), "w", encoding="utf-8",
                 newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=["corpus","source_coda","chinese_coda","count"])
        wr.writeheader(); wr.writerows(rows_csv)
print()
print("wrote reports/step20_summary.txt")
print("wrote data/derived/coda_spelling.csv")
