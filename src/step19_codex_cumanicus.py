# -*- coding: utf-8 -*-
"""
step19_codex_cumanicus.py
=========================
A third lexicon for the modern-echo test: the Cuman (Kipchak Turkic) of the
Codex Cumanicus, as edited by Geza Kuun (Budapest, 1880).

Why this one matters
--------------------
Steps 16-17 searched modern Turkish and Kazakh and found nothing above chance.
Step 18 repeated the search against Kasgarli Mahmud's Divanu Lugati't-Turk
(1072-77) and the noise floor rose while both known answers became visible.
The Codex adds a THIRD point on that line, and a different one:

  * it is Kipchak, not Karakhanid - a separate branch of Turkic;
  * it was compiled c. 1300 by Italian merchants and German missionaries,
    so its vocabulary was collected by outsiders, exactly as the Chinese
    scribes collected theirs;
  * Kuun's 1880 edition is PUBLIC DOMAIN, so unlike Clauson or the Kutadgu
    Bilig editions the derived lexicon here can be released with this work.

Input
-----
my_resources/lexicons/Codex_Cumanicus_Kuun_1880.zip
  - 550 OCR'd page files. Kuun prints four indices; pages 395-455 of the scan
    are the "Vocabularium cumanico-latinum", which is the one wanted. The
    Persian (456-500) and German (501-516) vocabularies are deliberately
    skipped - the Persian index in particular would inject Iranian vocabulary
    into a Turkic lexicon and quietly inflate the match rate.

A caution about the orthography
-------------------------------
Kuun's headwords keep the Codex's own spelling, which is 14th-century Italian
and German convention, not a phonemic transcription: c is usually k, ch is k,
x and cs are s-hat, j is y. The normalisation below is documented and
approximate. It is a source of error, and the null model is what keeps that
error honest - a sloppy normalisation makes the pseudo-names match better too.

Outputs
-------
data/derived/cuman_lexicon.csv
reports/step19_summary.txt
data/derived/cuman_echo.csv
"""
import csv, io, os, re, sys, random, collections, zipfile

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
DER  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
RES  = os.path.join(ROOT, "my_resources")
os.makedirs(REP, exist_ok=True)
random.seed(20260827)

# reuse step 16's transliteration, segmentation and scoring
src = io.open(os.path.join(HERE, "step16_modern_echo.py"), encoding="utf-8").read()
src = src.split("# ---------------------------------------------------------- lexicons")[0]
G = {"__name__": "_s16", "sys": sys, "os": os,
     "__file__": os.path.join(HERE, "step16_modern_echo.py")}
exec(compile(src, "step16", "exec"), G)
segment, to_turkish = G["segment"], G["to_turkish"]
_raw_sub, score = G["sub_cost"], G["score"]

# Later Han had no r-; step 15 shows source r- written l- in 12 of 14 cases.
def sub_cost(a, b):
    if {a, b} == {"l", "r"}: return 0.15
    return _raw_sub(a, b)
G["sub_cost"] = sub_cost
score.__globals__["sub_cost"] = sub_cost

out = []
def w(s=""):
    print(s); out.append(s)

# ------------------------------------------------------------------ input
def find_zip():
    for root, _d, files in os.walk(RES):
        for f in files:
            if f.lower().startswith("codex_cumanicus_kuun") and f.lower().endswith(".zip"):
                return os.path.join(root, f)
    return None

Z = find_zip()
if not Z:
    print("Codex_Cumanicus_Kuun_1880.zip not found under my_resources/"); sys.exit(1)

FIRST, LAST = 395, 455          # Vocabularium cumanico-latinum
def pages():
    with zipfile.ZipFile(Z) as z:
        names = [n for n in z.namelist() if n.endswith(".txt")]
        for n in sorted(names):
            base = os.path.basename(n)[:8]
            if base.isdigit() and FIRST <= int(base) <= LAST:
                yield int(base), z.read(n).decode("utf-8", "ignore")

# headword, gloss, then the codex page reference Kuun always prints
ENTRY = re.compile(
    r"^\s*([A-ZÁÉÍÓÚÄÖÜČŠŽ][A-Za-zÀ-ɏčšžğıíáéóú'’-]{1,22})"      # headword
    r"\s*[«\"]?\s*([^»\"]{2,60}?)[»\"]?\s*,?\s*"                   # latin gloss
    r"(?:pag\.|png\.)\s*(\d{1,3})")                                # page ref

def extract():
    rows, seen = [], set()
    for pno, text in pages():
        for line in text.split("\n"):
            m = ENTRY.match(line.rstrip())
            if not m: continue
            hw = m.group(1).strip("'’-")
            gl = re.sub(r"\s+", " ", m.group(2)).strip(" .,-«»\"")
            if len(hw) < 2 or not gl: continue
            key = hw.lower()
            if key in seen: continue
            seen.add(key)
            rows.append({"headword": hw, "gloss_lat": gl[:80],
                         "codex_page": m.group(3), "scan_page": pno})
    return rows

ROWS = extract()
with io.open(os.path.join(DER, "cuman_lexicon.csv"), "w", encoding="utf-8",
             newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=["headword", "gloss_lat", "codex_page", "scan_page"])
    wr.writeheader(); wr.writerows(ROWS)

# --------------------------------------------------- orthographic normalisation
# Codex spelling -> the letters step 16's segmenter expects. Longest first.
NORM = [("chi", "ki"), ("che", "ke"), ("ch", "k"), ("cs", "ş"), ("sch", "ş"),
        ("gh", "g"), ("qu", "k"), ("ci", "çi"), ("ce", "çe"),
        ("č", "ç"), ("š", "ş"), ("ž", "j"), ("ġ", "g"), ("ñ", "ng"), ("ŋ", "ng"),
        ("x", "ş"), ("c", "k"), ("j", "y"), ("w", "v"),
        ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ä", "e")]
def norm(x):
    s = x.lower()
    for a, b in NORM: s = s.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", s)

GLOSS, WORDS = {}, set()
for r in ROWS:
    n = norm(r["headword"])
    if 2 <= len(n) <= 14 and " " not in n:
        WORDS.add(n)
        GLOSS.setdefault(n, r["gloss_lat"])

# ------------------------------------------------------------------ index
ALLC = "bcçdfgğhjklmnprsştvyzŋ"
NEAR = {c: [d for d in ALLC if sub_cost(c, d) <= 0.55] for c in ALLC}
IDX = collections.defaultdict(list)
for x in WORDS:
    c, v = segment(x)
    if 1 <= len(c) <= 6: IDX[(len(c), c[0])].append((c, v, x))

def best(form, k=4):
    t_c, t_v = segment(form)
    if not t_c: return []
    heads = set(NEAR.get(t_c[0], [t_c[0]])) | {t_c[0]}
    if len(t_c) > 1: heads |= set(NEAR.get(t_c[1], [t_c[1]]))
    hits = []
    for L in (len(t_c) - 1, len(t_c), len(t_c) + 1):
        for h in heads:
            for c, v, x in IDX.get((L, h), ()):
                sc = score(t_c, t_v, c, v)
                if sc < 0.60: hits.append((sc, x))
    hits.sort()
    seen, res = set(), []
    for sc, x in hits:
        if x in seen: continue
        seen.add(x); res.append((round(sc, 3), x))
        if len(res) >= k: break
    return res

# ------------------------------------------------------------------ names
def read(p):
    with io.open(p, encoding="utf-8-sig") as fh: return list(csv.DictReader(fh))
NAMES = []
for fn in ("xiongnu_rulers_reconstructed.csv", "xiongnu_titles_lexicon_reconstructed.csv"):
    p = os.path.join(DER, fn)
    if os.path.exists(p):
        for r in read(p):
            lh = (r.get("lhan_schuessler") or "").strip()
            if lh and "PENDING" not in lh:
                NAMES.append({"chinese": r["chinese"], "pinyin": r.get("pinyin_modern", ""),
                              "lhan": lh, "turkish": to_turkish(lh)})

SYL  = [s for n in NAMES for s in n["lhan"].split() if s]
LENS = [max(1, len(n["lhan"].split())) for n in NAMES]
def pseudo():
    return to_turkish(" ".join(random.choice(SYL) for _ in range(random.choice(LENS))))

NULL_N = 300
nulls = sorted((best(pseudo(), k=1) or [(99.0, "")])[0][0] for _ in range(NULL_N))
def pval(s): return sum(1 for x in nulls if x <= s) / float(NULL_N)

w("=" * 74)
w(" STEP 19 - Xiongnu readings against the Codex Cumanicus (Kuun 1880)")
w("=" * 74)
w(" source                    : %s" % os.path.basename(Z))
w(" scan pages used           : %d-%d (Vocabularium cumanico-latinum)" % (FIRST, LAST))
w(" entries extracted         : %d" % len(ROWS))
w(" normalised search forms   : %d" % len(WORDS))
w(" names                     : %d" % len(NAMES))
w("")
w(" NULL: %d/%d meaningless pseudo-names found a match; median best score %.3f"
  % (sum(1 for x in nulls if x < 99.0), NULL_N, nulls[NULL_N // 2]))
w(" for comparison - modern Turkish 0.156, Kazakh 0.183, Divanu Lugati't-Turk 0.200")
w("")

w("=" * 74)
w(" THE TWO KNOWN ANSWERS")
w("=" * 74)
for ch, want, why in (("撑犁", "tengri", "Hanshu glosses it 天 'heaven'"),
                      ("頭曼", "tümen", "standard etymology")):
    n = [x for x in NAMES if x["chinese"] == ch]
    if not n: continue
    n = n[0]
    m = best(n["turkish"], k=5)
    w(" %s  %s  ->  %s   (%s)" % (ch, n["lhan"], n["turkish"], why))
    for i, (s, x) in enumerate(m, 1):
        mark = "   <== the known answer" if x == norm(want) else ""
        w("    %d. %-14s %.3f  %s%s" % (i, x, s, GLOSS.get(x, "")[:40], mark))
    present = norm(want) in WORDS
    rank = next((i for i, (s, x) in enumerate(best(n["turkish"], k=60), 1)
                 if x == norm(want)), None)
    w("    %s in lexicon: %s ; rank: %s"
      % (want, "yes" if present else "NOT PRESENT", rank if rank else "not returned"))
    w("")

w("=" * 74)
w(" ALL NAMES")
w("=" * 74)
rows, beat, withc = [], 0, 0
for n in NAMES:
    m = best(n["turkish"], k=3)
    w("%s  %-22s %-24s -> %s" % (n["chinese"], n["pinyin"][:22], n["lhan"][:24], n["turkish"]))
    if not m:
        w("     no candidate"); w(""); continue
    withc += 1
    p = pval(m[0][0])
    if p <= 0.05: beat += 1
    for s, x in m:
        w("     %-14s %.3f  p=%.3f  %s" % (x, s, p, GLOSS.get(x, "")[:46]))
        rows.append({"chinese": n["chinese"], "pinyin": n["pinyin"], "lhan": n["lhan"],
                     "turkish_render": n["turkish"], "candidate": x,
                     "gloss_lat": GLOSS.get(x, ""), "score": s,
                     "p_vs_null": round(p, 4),
                     "beats_chance": "yes" if p <= 0.05 else "no"})
    w("")
w("=" * 74)
w(" %d of %d names with a candidate beat chance at p<=0.05." % (beat, withc))
w("=" * 74)

with io.open(os.path.join(REP, "step19_summary.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
with io.open(os.path.join(DER, "cuman_echo.csv"), "w", encoding="utf-8", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    wr.writeheader(); wr.writerows(rows)
print()
print("wrote data/derived/cuman_lexicon.csv")
print("wrote reports/step19_summary.txt")
print("wrote data/derived/cuman_echo.csv")
