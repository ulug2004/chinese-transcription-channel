# -*- coding: utf-8 -*-
"""
step16_modern_echo.py
=====================
Do the Later Han readings of the Xiongnu names resemble modern Turkic words
more than chance allows?

This is the most dangerous question in the project, because it always
"works". Turkish has ~370,000 dictionary entries; any 39 short strings will
find striking-looking matches in it. So the search is only meaningful next to
a null model that runs the SAME search on names that cannot mean anything.

Method
------
1. Each Later Han reading is transliterated into Turkish orthography.
2. Candidates are scored on their CONSONANT SKELETON, because that is the
   part of the signal that survives (step 14: initials 79-94%, nasal codas
   99%, vowels 50%, stop codas 0%). Costs follow those measurements:
     - voicing differences are cheap  (transcription is loose on voicing)
     - a missing final stop is cheap  (stop codas do not survive at all)
     - place/manner differences are expensive
     - vowel mismatches carry 1/4 weight
3. NULL: pseudo-names are built by resampling Later Han syllables from the
   same 39 names, then run through the identical search. A real name is only
   reported if its best match beats what chance produces.

Outputs
-------
reports/step16_summary.txt
data/derived/modern_echo_candidates.csv

Usage
-----
    python step16_modern_echo.py [project_root]
"""

import csv, io, os, re, sys, random, collections

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))
DER = os.path.join(ROOT, "data", "derived")
REP = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)
random.seed(20260827)          # fixed: results are reproducible

out = []
def w(s=""):
    print(s); out.append(s)

# ---------------------------------------------------------- transliteration
MAP = [("tśʰ","ç"),("tś","ç"),("dź","c"),("kʰ","k"),("tʰ","t"),("pʰ","p"),
       ("ɑ","a"),("ə","ı"),("ɨ","ı"),("ɔ","o"),("ɛ","e"),
       ("ś","ş"),("ṣ","ş"),("ź","j"),("ŋ","ng"),("ń","ny"),("ɣ","ğ"),
       ("ḍ","d"),("ṭ","t"),("ṇ","n"),("j","y"),("w","v"),("ʔ","’"),
       ("ᴬ",""),("ᴮ",""),("ᶜ",""),("ᴰ",""),("ʰ","")]

def to_turkish(lh):
    s = lh
    for a, b in MAP:
        s = s.replace(a, b)
    return s

# ---------------------------------------------------------- phonology
VOW = set("aeıioöuü")
DIG = {"ng": "ŋ"}
def segment(word):
    """Turkish orthography -> (consonant skeleton, vowel string)."""
    s = word.lower().replace("’", "").replace("'", "")
    s = re.sub(r"[^a-zçğışöü ]", "", s).replace(" ", "")
    cons, vows, i = [], [], 0
    while i < len(s):
        two = s[i:i+2]
        if two in DIG:
            cons.append(DIG[two]); i += 2; continue
        ch = s[i]
        (vows if ch in VOW else cons).append(ch)
        i += 1
    return "".join(cons), "".join(vows)

VOICE = [("p","b"),("t","d"),("k","g"),("ç","c"),("s","z"),("ş","j"),("f","v")]
PAIR = {}
for a, b in VOICE:
    PAIR[a] = b; PAIR[b] = a

MANNER = {}
for c in "pbtdkgcç": MANNER[c] = "stop"
for c in "fvszşjğh": MANNER[c] = "fric"
for c in "mnŋ":      MANNER[c] = "nasal"
for c in "lr":       MANNER[c] = "liquid"
for c in "y":        MANNER[c] = "glide"

PLACE = {"p":"lab","b":"lab","m":"lab","f":"lab","v":"lab",
         "t":"cor","d":"cor","s":"cor","z":"cor","n":"cor","l":"cor","r":"cor",
         "ş":"post","j":"post","ç":"post","c":"post","y":"post",
         "k":"vel","g":"vel","ğ":"vel","ŋ":"vel","h":"vel"}

STOPS = set("pbtdkgçc")
GLIDEY = set("yğvh")

def sub_cost(a, b):
    if a == b: return 0.0
    if PAIR.get(a) == b: return 0.30                       # voicing only
    if MANNER.get(a) == MANNER.get(b):
        return 0.55 if PLACE.get(a) == PLACE.get(b) else 0.85
    return 1.0

def indel_cost(c, final):
    if final and c in STOPS: return 0.30                   # step 14: coda stops lost
    if c in GLIDEY: return 0.55
    return 1.0

def skel_dist(a, b):
    """Weighted edit distance between two consonant skeletons."""
    la, lb = len(a), len(b)
    prev = [0.0] * (lb + 1)
    for j in range(1, lb + 1):
        prev[j] = prev[j-1] + indel_cost(b[j-1], j == lb)
    for i in range(1, la + 1):
        cur = [prev[0] + indel_cost(a[i-1], i == la)] + [0.0] * lb
        for j in range(1, lb + 1):
            cur[j] = min(prev[j-1] + sub_cost(a[i-1], b[j-1]),
                         prev[j] + indel_cost(a[i-1], i == la),
                         cur[j-1] + indel_cost(b[j-1], j == lb))
        prev = cur
    return prev[lb]

def vow_pen(a, b):
    n = min(len(a), len(b))
    if n == 0: return 0.5
    bad = sum(1 for i in range(n) if a[i] != b[i]) + abs(len(a) - len(b))
    return 0.25 * bad / max(len(a), len(b))

def score(t_c, t_v, c_c, c_v):
    if abs(len(t_c) - len(c_c)) > 1: return 99.0
    if not t_c or not c_c: return 99.0
    return (skel_dist(t_c, c_c) + vow_pen(t_v, c_v)) / max(len(t_c), len(c_c))

# ---------------------------------------------------------- lexicons
def load_hunspell(path, translit=None):
    words = set()
    if not os.path.exists(path): return words
    with io.open(path, encoding="utf-8", errors="ignore") as fh:
        for i, line in enumerate(fh):
            if i == 0: continue
            wd = line.split("/")[0].strip().lower()
            if not wd or " " in wd or "-" in wd: continue
            if translit: wd = translit(wd)
            if 2 <= len(wd) <= 14: words.add(wd)
    return words

KK = {"а":"a","ә":"ä","б":"b","в":"v","г":"g","ғ":"ğ","д":"d","е":"e","ё":"yo",
      "ж":"j","з":"z","и":"i","й":"y","к":"k","қ":"k","л":"l","м":"m","н":"n",
      "ң":"ng","о":"o","ө":"ö","п":"p","р":"r","с":"s","т":"t","у":"u","ұ":"u",
      "ү":"ü","ф":"f","х":"h","һ":"h","ц":"ts","ч":"ç","ш":"ş","щ":"şç","ъ":"",
      "ы":"ı","і":"i","ь":"","э":"e","ю":"yu","я":"ya"}
def kk_latin(s):
    return "".join(KK.get(c, c) for c in s)

def find_hunspell():
    """Look for Hunspell .dic files in the usual places, project first."""
    cands = []
    env = os.environ.get("HUNSPELL_DIR")
    if env: cands.append(env)
    cands += [os.path.join(ROOT, "data", "external", "hunspell"),
              "/usr/share/hunspell", "/usr/share/myspell",
              r"C:\Program Files\LibreOffice\share\extensions",
              r"C:\Program Files (x86)\LibreOffice\share\extensions"]
    for d in cands:
        if d and os.path.isdir(d):
            for root, _dirs, files in os.walk(d):
                if any(f.endswith(".dic") for f in files):
                    return d
    return None

HUN = find_hunspell()
if HUN is None:
    print("No Hunspell dictionaries found.\n"
          "Put tr_TR.dic and kk_KZ.dic in data/external/hunspell/ , or set\n"
          "HUNSPELL_DIR. Sources:\n"
          "  Turkish  https://github.com/tdd-ai/hunspell-tr\n"
          "  Kazakh   https://github.com/kergalym/myspell-kk\n"
          "  Kyrgyz   https://github.com/apertium/apertium-kir (morphological, not hunspell)")
    sys.exit(1)

def dic(name):
    """Locate a .dic anywhere under HUN."""
    for root, _dirs, files in os.walk(HUN):
        if name in files:
            return os.path.join(root, name)
    return os.path.join(HUN, name)


# Frequency filter: a "modern equivalent" should be a word people actually
# use, not an obscure entry that happens to fit. wordfreq's Turkish list is
# the intersection filter; it takes 292k hunspell lemmas down to ~23k.
try:
    from wordfreq import zipf_frequency
    HAVEFREQ = True
except Exception:
    HAVEFREQ = False

LEX = {}
tr = load_hunspell(dic("tr_TR.dic"))
if tr:
    if HAVEFREQ:
        tr = set(x for x in tr if zipf_frequency(x, "tr") >= 2.5)
    LEX["Turkish"] = tr

kk = load_hunspell(dic("kk_KZ.dic"), kk_latin)
if kk: LEX["Kazakh"] = kk

# index: (skeleton length, first consonant) -> [(skeleton, vowels, word)]
INDEX = {}
for lang, words in LEX.items():
    idx = collections.defaultdict(list)
    for wd in words:
        c, v = segment(wd)
        if 1 <= len(c) <= 6:
            idx[(len(c), c[0])].append((c, v, wd))
    INDEX[lang] = idx

ALLC = "bcçdfgğhjklmnprsştvyzŋ"
NEAR = {c: [d for d in ALLC if sub_cost(c, d) <= 0.55] for c in ALLC}

# ---------------------------------------------------------- search
def best_matches(turkish_form, lang, k=3):
    t_c, t_v = segment(turkish_form)
    if not t_c: return []
    heads = set(NEAR.get(t_c[0], [t_c[0]]))
    heads.add(t_c[0])
    if len(t_c) > 1:                       # allow an initial that was dropped
        heads.update(NEAR.get(t_c[1], [t_c[1]]))
    hits = []
    for L in (len(t_c) - 1, len(t_c), len(t_c) + 1):
        for h in heads:
            for c, v, wd in INDEX[lang].get((L, h), ()):
                sc = score(t_c, t_v, c, v)
                if sc < 0.60:
                    hits.append((sc, wd))
    hits.sort()
    seen, outl = set(), []
    for sc, wd in hits:
        if wd in seen: continue
        seen.add(wd); outl.append((round(sc, 3), wd))
        if len(outl) >= k: break
    return outl

# ---------------------------------------------------------- data
def read(p):
    with io.open(p, encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))

rows = []
for fn, kind in (("xiongnu_rulers_reconstructed.csv", "ruler/clan"),
                 ("xiongnu_titles_lexicon_reconstructed.csv", "title/lexical")):
    p = os.path.join(DER, fn)
    if os.path.exists(p):
        for r in read(p):
            lh = (r.get("lhan_schuessler") or "").strip()
            if lh and "PENDING" not in lh:
                rows.append({"chinese": r["chinese"], "pinyin": r.get("pinyin_modern", ""),
                             "kind": kind, "lhan": lh, "turkish": to_turkish(lh)})

w("=" * 72)
w(" STEP 16 - modern Turkic echoes of the Xiongnu readings, against a null")
w("=" * 72)
w(" lexicons: " + ", ".join("%s %d entries" % (k, len(v)) for k, v in LEX.items()))
w(" names   : %d" % len(rows))
w("")

# ---------------------------------------------------------- null model
SYL = []
for r in rows:
    SYL.extend([s for s in r["lhan"].split() if s])
LENS = [max(1, len(r["lhan"].split())) for r in rows]

def pseudo():
    n = random.choice(LENS)
    return to_turkish(" ".join(random.choice(SYL) for _ in range(n)))

NULL_N = 300
NULL = {}
for lang in LEX:
    scores = []
    for _ in range(NULL_N):
        m = best_matches(pseudo(), lang, k=1)
        scores.append(m[0][0] if m else 99.0)
    scores.sort()
    NULL[lang] = scores
    got = sum(1 for s in scores if s < 99.0)
    w(" NULL (%s): %d/%d pseudo-names found a match under 0.60; "
      "median best score %.3f, 5th percentile %.3f"
      % (lang, got, NULL_N, scores[NULL_N // 2],
         scores[max(0, int(0.05 * NULL_N))]))
w("")
w(" A pseudo-name is built by resampling Later Han syllables from these same")
w(" names, so it has the right shape and the right sound inventory and cannot")
w(" mean anything. p = fraction of pseudo-names scoring at least as well.")
w("")

def pval(lang, s):
    sc = NULL[lang]
    return sum(1 for x in sc if x <= s) / float(len(sc))

# ---------------------------------------------------------- report
csv_rows = []
w("-" * 72)
for r in rows:
    line = "%s  %-26s  LH %-28s  TR %s" % (r["chinese"], r["pinyin"][:26],
                                           r["lhan"][:28], r["turkish"])
    w(line)
    any_hit = False
    for lang in LEX:
        mm = best_matches(r["turkish"], lang, k=3)
        if not mm: continue
        p = pval(lang, mm[0][0])
        flag = "  <== beats chance" if p <= 0.05 else ("  (chance level)" if p > 0.20 else "")
        w("     %-8s %s   p=%.3f%s" % (lang,
          ", ".join("%s [%.2f]" % (wd, s) for s, wd in mm), p, flag))
        any_hit = True
        for s, wd in mm:
            csv_rows.append({"chinese": r["chinese"], "pinyin": r["pinyin"],
                             "kind": r["kind"], "lhan": r["lhan"],
                             "turkish_render": r["turkish"], "language": lang,
                             "candidate": wd, "score": s,
                             "p_vs_null": round(p, 4),
                             "beats_chance": "yes" if p <= 0.05 else "no"})
    if not any_hit:
        w("     no candidate under threshold in any lexicon")
    w("")

sig = [c for c in csv_rows if c["beats_chance"] == "yes"]
w("=" * 72)
w(" %d of %d name-language pairs produced a best match that beats chance at"
  " p<=0.05." % (len({(c['chinese'], c['language']) for c in sig}), len(rows) * len(LEX)))
w(" Everything else is at or near the rate a meaningless string achieves.")
w("=" * 72)

with io.open(os.path.join(REP, "step16_summary.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
with io.open(os.path.join(DER, "modern_echo_candidates.csv"), "w",
             encoding="utf-8", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=["chinese", "pinyin", "kind", "lhan",
                                        "turkish_render", "language", "candidate",
                                        "score", "p_vs_null", "beats_chance"])
    wr.writeheader(); wr.writerows(csv_rows)
print()
print("wrote reports/step16_summary.txt")
print("wrote data/derived/modern_echo_candidates.csv")
