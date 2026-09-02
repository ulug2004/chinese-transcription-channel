# -*- coding: utf-8 -*-
"""
step18_old_turkic.py
====================
Repeat the modern-echo search (steps 16-17) against an ELEVENTH-CENTURY
Turkic dictionary instead of a modern one.

Why this is the right lexicon
-----------------------------
Steps 16-17 searched modern Turkish and Kazakh and found nothing above
chance. Two objections were raised and both are sound:

  * the matches were loanwords - kauçuk is French caoutchouc, and a
    2nd-century BCE steppe name cannot echo a 19th-century borrowing;
  * modern Turkish is 2,000 years downstream of the Xiongnu.

Kaşgarli Mahmud's Divanu Lugati't-Turk (1072-77) answers both. It is a
dictionary of Karakhanid Turkic compiled a thousand years closer to the
period, it contains no European loans whatever, and it is small - which
RAISES the noise floor for free (step 17 showed the floor climbing from
0.156 to 0.372 as the lexicon shrank).

It also carries glosses, so a candidate arrives with its meaning attached
instead of being looked up afterwards - and crucially it contains both words
this project can check against a known answer:

    teñri   'gök, sema' (sky, heaven)   <- the Hanshu glosses 撑犁 as 天
    tümen   'pek çok' (very many)       <- the standard reading of 頭曼

Input
-----
my_resources/Divanu-Lugatit-Turk-Dizini-2MB.pdf   (TDK index volume; the
text layer is machine-readable, so no OCR is needed)

Outputs
-------
data/derived/dlt_lexicon.csv
reports/step18_summary.txt
data/derived/old_turkic_echo.csv
"""
import csv, io, os, re, sys, random, collections, warnings
warnings.filterwarnings("ignore")

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
DER = os.path.join(ROOT, "data", "derived")
REP = os.path.join(ROOT, "reports")
RES = os.path.join(ROOT, "my_resources")
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
_raw_sub = G["sub_cost"]

# Later Han Chinese had no r-. Step 15's correspondence table shows source r-
# written with a Chinese l- character in 12 of 14 attestations across the three
# corpora (Mongolian 3/4, Sanskrit 9/10). So an l facing an r is not a mismatch
# here - it is the expected spelling, and is priced accordingly rather than by
# the generic same-manner rule.
def sub_cost(a, b):
    if {a, b} == {"l", "r"}: return 0.15
    return _raw_sub(a, b)
G["sub_cost"] = sub_cost
G["score"].__globals__["sub_cost"] = sub_cost
score = G["score"]

out = []
def w(s=""):
    print(s); out.append(s)

# ------------------------------------------------------------ extract DLT
def find_dlt():
    """The index PDF, wherever it sits under my_resources."""
    name = "Divanu-Lugatit-Turk-Dizini-2MB.pdf"
    direct = os.path.join(RES, name)
    if os.path.exists(direct):
        return direct
    for root, _dirs, files in os.walk(RES):
        for f in files:
            if f == name or (f.startswith("Divanu-Lugatit-Turk-Dizini")
                             and f.lower().endswith(".pdf")):
                return os.path.join(root, f)
    return direct

PDF = find_dlt()
TRL = "abcçdefgğhıijklmnoöprsştuüvyzñŋ"
ENTRY = re.compile(r"^([%s][%s ]{1,24}?)\s{2,}(\S.*)$" % (TRL, TRL))

def extract():
    import pypdf
    r = pypdf.PdfReader(PDF)
    seen, rows = {}, []
    for i, pg in enumerate(r.pages):
        for line in (pg.extract_text() or "").split("\n"):
            m = ENTRY.match(line.rstrip())
            if not m: continue
            hw, gl = m.group(1).strip(), m.group(2).strip()
            if len(hw) < 2: continue
            gloss = re.split(r"[·;]\s*[IVX]+,|\s[IVX]+,\s*\d", gl)[0].strip(" ·,;")
            if hw not in seen:
                seen[hw] = True
                rows.append({"headword": hw, "gloss_tr": gloss[:120],
                             "raw": gl[:200], "pdf_page": i + 1})
    return rows

if not os.path.exists(PDF):
    print("Divanu-Lugatit-Turk-Dizini-2MB.pdf not found in my_resources/")
    sys.exit(1)

ROWS = extract()
with io.open(os.path.join(DER, "dlt_lexicon.csv"), "w", encoding="utf-8",
             newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=["headword", "gloss_tr", "raw", "pdf_page"])
    wr.writeheader(); wr.writerows(ROWS)

# ñ is the velar nasal. Write it "ng" - the same two letters step 16 produces
# from Chinese -ng - so both sides reach the segmenter in one spelling. Writing
# it as a bare ŋ silently loses it: the segmenter's character filter drops it.
def norm(x): return x.replace("ñ", "ng").replace("ŋ", "ng")

GLOSS = {norm(r["headword"]): r["gloss_tr"] for r in ROWS}
WORDS = {h for h in GLOSS if " " not in h and 2 <= len(h) <= 14}

# ------------------------------------------------------------ index
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

# ------------------------------------------------------------ names
def read(p):
    with io.open(p, encoding="utf-8-sig") as fh: return list(csv.DictReader(fh))
NAMES = []
for fn in ("xiongnu_rulers_reconstructed.csv", "xiongnu_titles_lexicon_reconstructed.csv"):
    p = os.path.join(DER, fn)
    if os.path.exists(p):
        for r in read(p):
            lh = (r.get("lhan_schuessler") or "").strip()
            if lh and "PENDING" not in lh:
                NAMES.append({"chinese": r["chinese"],
                              "pinyin": r.get("pinyin_modern", ""),
                              "lhan": lh, "turkish": to_turkish(lh)})

SYL = [s for n in NAMES for s in n["lhan"].split() if s]
LENS = [max(1, len(n["lhan"].split())) for n in NAMES]
def pseudo():
    return to_turkish(" ".join(random.choice(SYL)
                               for _ in range(random.choice(LENS))))

NULL_N = 300
nulls = []
for _ in range(NULL_N):
    m = best(pseudo(), k=1)
    nulls.append(m[0][0] if m else 99.0)
nulls.sort()
def pval(s): return sum(1 for x in nulls if x <= s) / float(NULL_N)

w("=" * 74)
w(" STEP 18 - Xiongnu readings against Divanu Lugati't-Turk (1072-77)")
w("=" * 74)
w(" index entries parsed      : %d" % len(ROWS))
w(" single-word headwords used: %d" % len(WORDS))
w(" names                     : %d" % len(NAMES))
w("")
w(" NULL: %d/%d meaningless pseudo-names found a match; median best score %.3f"
  % (sum(1 for x in nulls if x < 99.0), NULL_N, nulls[NULL_N // 2]))
w(" (modern Turkish, step 17, for comparison: 231/250, median 0.156)")
w("")

# ------------------------------------------------------------ known answers
w("=" * 74)
w(" THE TWO KNOWN ANSWERS")
w("=" * 74)
for ch, want, why in (("撑犁", norm("teñri"), "Hanshu glosses it 天 'heaven'"),
                      ("頭曼", "tümen", "standard etymology")):
    n = [x for x in NAMES if x["chinese"] == ch]
    if not n: continue
    n = n[0]
    m = best(n["turkish"], k=5)
    w(" %s  %s  ->  %s      (%s)" % (ch, n["lhan"], n["turkish"], why))
    for i, (s, x) in enumerate(m, 1):
        mark = "   <== the known answer" if x == want else ""
        w("    %d. %-12s %.3f   %s%s" % (i, x, s, GLOSS.get(x, "")[:44], mark))
    inlex = "yes" if want in WORDS else "NOT IN LEXICON"
    rank = next((i for i, (s, x) in enumerate(best(n["turkish"], k=50), 1)
                 if x == want), None)
    w("    %s in lexicon: %s ; rank among all candidates: %s"
      % (want, inlex, rank if rank else "not returned"))
    w("")

# ------------------------------------------------------------ all names
w("=" * 74)
w(" ALL NAMES")
w("=" * 74)
rows = []
beat = withc = 0
for n in NAMES:
    m = best(n["turkish"], k=3)
    w("%s  %-24s %-26s -> %s" % (n["chinese"], n["pinyin"][:24],
                                 n["lhan"][:26], n["turkish"]))
    if not m:
        w("     no candidate"); w(""); continue
    withc += 1
    p = pval(m[0][0])
    if p <= 0.05: beat += 1
    for s, x in m:
        w("     %-12s %.3f  p=%.3f  %s" % (x, s, p, GLOSS.get(x, "")[:52]))
        rows.append({"chinese": n["chinese"], "pinyin": n["pinyin"],
                     "lhan": n["lhan"], "turkish_render": n["turkish"],
                     "candidate": x, "gloss_tr": GLOSS.get(x, ""),
                     "score": s, "p_vs_null": round(p, 4),
                     "beats_chance": "yes" if p <= 0.05 else "no"})
    w("")

w("=" * 74)
w(" %d of %d names with a candidate beat chance at p<=0.05." % (beat, withc))
w("=" * 74)

with io.open(os.path.join(REP, "step18_summary.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(out) + "\n")
with io.open(os.path.join(DER, "old_turkic_echo.csv"), "w", encoding="utf-8",
             newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    wr.writeheader(); wr.writerows(rows)
print()
print("wrote data/derived/dlt_lexicon.csv")
print("wrote reports/step18_summary.txt")
print("wrote data/derived/old_turkic_echo.csv")
