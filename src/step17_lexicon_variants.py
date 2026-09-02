# -*- coding: utf-8 -*-
"""
step17_lexicon_variants.py
==========================
Does changing the dictionary rescue the modern-echo search?

Two objections to step 16 are worth testing rather than arguing about:

  (a) "Most of the matches are loanwords - kauçuk is French caoutchouc. A
       2nd-century BCE steppe name cannot echo a word Turkish borrowed from
       French. Filter to native Turkic vocabulary."
  (b) "Search Turkish AND Kazakh together. Two dictionaries should give a
       better statistical match than one."

Both are testable. The catch in (b) is that the null moves with the lexicon:
a bigger word list finds more matches for the real names AND for meaningless
strings, so raw match counts always improve while the p-value need not.

Variants tested
---------------
  turkish        Turkish lemmas in common use
  kazakh         Kazakh lemmas (Cyrillic, transliterated)
  union          turkish + kazakh          (objection b, as usually meant)
  turkish_native turkish minus loan-shaped words   (objection a)
  intersect      words present in BOTH lists       (objection b, done right)
  intersect_nat  intersect + the native filter

Native filter (a phonotactic proxy, not an etymological dictionary):
  - drops words beginning f, l, r, z, j, v, h - native Turkic words do not
  - drops any word containing f or j - non-native phonemes
  - drops â î û - Arabic/Persian long vowels
  - drops final b, c, d, g - native finals devoice (kitap, not kitab)
  - drops initial consonant clusters
  - requires vowel harmony - all vowels front, or all back

Outputs
-------
reports/step17_summary.txt
data/derived/lexicon_variants.csv
"""
import csv, io, os, re, sys, random, collections

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
DER = os.path.join(ROOT, "data", "derived")
REP = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)
random.seed(20260827)

# reuse step 16's transliteration, segmentation and scoring
src = io.open(os.path.join(HERE, "step16_modern_echo.py"), encoding="utf-8").read()
src = src.split("# ---------------------------------------------------------- lexicons")[0]
# __file__ must be supplied: step 16 derives its own paths from it, and a
# name that exists in a normal script does NOT exist inside exec().
G = {"__name__": "_s16", "sys": sys, "os": os,
     "__file__": os.path.join(HERE, "step16_modern_echo.py")}
exec(compile(src, "step16", "exec"), G)
segment, score, to_turkish = G["segment"], G["score"], G["to_turkish"]
sub_cost = G["sub_cost"]

out = []
def w(s=""):
    print(s); out.append(s)

# ---------------------------------------------------------------- lexicons
def load(path, tl=None):
    ws = set()
    if not os.path.exists(path): return ws
    for i, line in enumerate(io.open(path, encoding="utf-8", errors="ignore")):
        if i == 0: continue
        x = line.split("/")[0].strip().lower()
        if not x or " " in x or "-" in x: continue
        if tl: x = tl(x)
        if 2 <= len(x) <= 14: ws.add(x)
    return ws

KKMAP = {"а":"a","ә":"ä","б":"b","в":"v","г":"g","ғ":"ğ","д":"d","е":"e","ё":"yo",
         "ж":"j","з":"z","и":"i","й":"y","к":"k","қ":"k","л":"l","м":"m","н":"n",
         "ң":"ng","о":"o","ө":"ö","п":"p","р":"r","с":"s","т":"t","у":"u","ұ":"u",
         "ү":"ü","ф":"f","х":"h","һ":"h","ц":"ts","ч":"ç","ш":"ş","щ":"şç","ъ":"",
         "ы":"ı","і":"i","ь":"","э":"e","ю":"yu","я":"ya"}
def kk_latin(s): return "".join(KKMAP.get(c, c) for c in s)

FRONT, BACK = set("eiöü"), set("aıou")
VOW = FRONT | BACK
BAD_INIT = set("flrzjvh")
CONS = "bcçdfgğhjklmnprsştvyz"
def native(x):
    if not x or x[0] in BAD_INIT: return False
    if "f" in x or "j" in x: return False
    if re.search(r"[âîû]", x): return False
    if x[-1] in "bcdg": return False
    if re.match(r"^[" + CONS + r"]{2}", x): return False
    vs = [c for c in x if c in VOW]
    if not vs: return False
    if any(v in FRONT for v in vs) and any(v in BACK for v in vs): return False
    return True

HUN = G["find_hunspell"]() if "find_hunspell" in G else "/usr/share/hunspell"
def dic(n):
    for root, _d, files in os.walk(HUN):
        if n in files: return os.path.join(root, n)
    return os.path.join(HUN, n)

TR = load(dic("tr_TR.dic"))
try:
    from wordfreq import zipf_frequency
    TR = {x for x in TR if zipf_frequency(x, "tr") >= 2.5}
except Exception:
    pass
KK = load(dic("kk_KZ.dic"), kk_latin)

VARIANTS = collections.OrderedDict([
    ("turkish",         TR),
    ("kazakh",          KK),
    ("union",           TR | KK),
    ("turkish_native",  {x for x in TR if native(x)}),
    ("intersect",       TR & KK),
    ("intersect_nat",   {x for x in (TR & KK) if native(x)}),
])

ALLC = "bcçdfgğhjklmnprsştvyzŋ"
NEAR = {c: [d for d in ALLC if sub_cost(c, d) <= 0.55] for c in ALLC}

def build(words):
    idx = collections.defaultdict(list)
    for x in words:
        c, v = segment(x)
        if 1 <= len(c) <= 6: idx[(len(c), c[0])].append((c, v, x))
    return idx

def best(form, idx, k=3):
    t_c, t_v = segment(form)
    if not t_c: return []
    heads = set(NEAR.get(t_c[0], [t_c[0]])) | {t_c[0]}
    if len(t_c) > 1: heads |= set(NEAR.get(t_c[1], [t_c[1]]))
    hits = []
    for L in (len(t_c) - 1, len(t_c), len(t_c) + 1):
        for h in heads:
            for c, v, x in idx.get((L, h), ()):
                sc = score(t_c, t_v, c, v)
                if sc < 0.60: hits.append((sc, x))
    hits.sort()
    seen, res = set(), []
    for sc, x in hits:
        if x in seen: continue
        seen.add(x); res.append((round(sc, 3), x))
        if len(res) >= k: break
    return res

# ---------------------------------------------------------------- names
def read(p):
    with io.open(p, encoding="utf-8-sig") as fh: return list(csv.DictReader(fh))
NAMES = []
for fn in ("xiongnu_rulers_reconstructed.csv", "xiongnu_titles_lexicon_reconstructed.csv"):
    p = os.path.join(DER, fn)
    if os.path.exists(p):
        for r in read(p):
            lh = (r.get("lhan_schuessler") or "").strip()
            if lh and "PENDING" not in lh:
                NAMES.append({"chinese": r["chinese"], "lhan": lh,
                              "turkish": to_turkish(lh)})
SYL = [s for n in NAMES for s in n["lhan"].split() if s]
LENS = [max(1, len(n["lhan"].split())) for n in NAMES]
def pseudo():
    return to_turkish(" ".join(random.choice(SYL)
                               for _ in range(random.choice(LENS))))
NULL_N = 250

KNOWN = {"撑犁": ("tengri", "tanrı"), "頭曼": ("tümen", "tuman")}

w("=" * 74)
w(" STEP 17 — does a different dictionary rescue the modern-echo search?")
w("=" * 74)
w(" %d names, null = %d resampled pseudo-names per variant" % (len(NAMES), NULL_N))
w("")
w(" %-16s %8s %9s %10s %12s" % ("variant", "entries", "null hit", "null med.",
                                "names p<=.05"))
w(" " + "-" * 60)

rows = []
for vname, words in VARIANTS.items():
    idx = build(words)
    nulls = []
    for _ in range(NULL_N):
        m = best(pseudo(), idx, k=1)
        nulls.append(m[0][0] if m else 99.0)
    nulls.sort()
    hit = sum(1 for x in nulls if x < 99.0)
    med = nulls[NULL_N // 2]
    def pval(s): return sum(1 for x in nulls if x <= s) / float(NULL_N)

    beat, withcand = 0, 0
    detail = {}
    for n in NAMES:
        m = best(n["turkish"], idx, k=3)
        if not m: continue
        withcand += 1
        p = pval(m[0][0])
        if p <= 0.05: beat += 1
        detail[n["chinese"]] = (m, p)
    w(" %-16s %8d %8d/%d %10.3f %8d of %d" % (vname, len(words), hit, NULL_N,
                                              med, beat, withcand))
    rows.append({"variant": vname, "entries": len(words), "null_hits": hit,
                 "null_n": NULL_N, "null_median": round(med, 3),
                 "names_beating_chance": beat, "names_with_candidate": withcand})
    VARIANTS[vname] = (words, idx, detail, nulls)

w("")
w(" 'null hit' = meaningless pseudo-names that still found a dictionary match.")
w(" 'null med.' = median best score for those pseudo-names; LOWER is a closer")
w(" match, so a lower median means the lexicon is noisier, not better.")
w("")
w("=" * 74)
w(" THE TWO KNOWN ANSWERS, ACROSS VARIANTS")
w("=" * 74)
for ch, targets in KNOWN.items():
    w(" %s  (known: %s)" % (ch, " / ".join(targets)))
    for vname in VARIANTS:
        words, idx, detail, nulls = VARIANTS[vname]
        if ch not in detail: 
            w("   %-16s no candidate"%vname); continue
        m, p = detail[ch]
        found = [t for t in targets if t in words]
        w("   %-16s top: %-28s p=%.3f   known form in lexicon: %s"
          % (vname, ", ".join("%s [%.2f]" % (x, s) for s, x in m), p,
             ", ".join(found) if found else "ABSENT"))
    w("")

with io.open(os.path.join(REP, "step17_summary.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
with io.open(os.path.join(DER, "lexicon_variants.csv"), "w",
             encoding="utf-8", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    wr.writeheader(); wr.writerows(rows)
print()
print("wrote reports/step17_summary.txt")
print("wrote data/derived/lexicon_variants.csv")
