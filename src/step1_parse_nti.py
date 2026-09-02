#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 1 - build the transcription training set from the NTI / Fo Guang Shan
Buddhist dictionary.

The corpus mixes two very different things:
    音譯 transcription : 釋迦牟尼 = sakyamuni   (phonetic - what we want)
    意譯 calque        : 大乘     = mahayana    (semantic - poison for the model)

Separating them is the whole job. Two approaches were tried and rejected:

  1. "Is the character in a known transcription-character set?" - bootstrapping on
     membership swallows common semantic characters (佛 天 王 生 見), after which
     everything scores 1.0 and calques like 福慧 = punya slip through.
  2. Character exclusivity (what share of a character's uses are phonetic) -
     punishes exactly the characters that do double duty, which is most of them.
     Collapsed to 67 pairs at 38% recall on the dictionary's own seed.

What works is PHONETIC VERIFICATION. Align characters to Sanskrit syllables and
check each character's Later Han reading against its syllable's onset:

    摩睺羅迦 = mahoraga   摩*ma 睺*ɦo 羅*la 迦*ka   -> 4/4 = 1.00  transcription
    福慧     = punya      福*puk ok, 慧*ɦuei vs nya -> 1/2 = 0.50  calque

Requires LHantab.tsv and Unihan.zip in data/external.
Stdlib only. Writes to data/derived/ and reports/.
"""
import csv, os, re, sys, zipfile
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT  = os.path.join(ROOT, "data", "external")
OUT  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
for d in (OUT, REP): os.makedirs(d, exist_ok=True)

CJK = re.compile(r'[㐀-䶿一-鿿豈-﫿]')
SKT = re.compile(r'Sanskrit(?:\s+equivalent)?\s*:\s*([^;,()\[\]]+)', re.I)

log_lines = []
def log(s=""):
    print(s); log_lines.append(s)

# ------------------------------------------------------- Sanskrit syllables
SKT_C = ['kh','gh','ch','jh','ṭh','ḍh','th','dh','ph','bh',
         'k','g','ṅ','c','j','ñ','ṭ','ḍ','ṇ','t','d','n','p','b','m',
         'y','r','l','v','ś','ṣ','s','h','ṃ','ḥ']
SKT_V = ['ai','au','ā','ī','ū','ṝ','ṛ','ḹ','ḷ','a','i','u','e','o']

def skt_onsets(w):
    """Split a Sanskrit word into syllables; return each syllable's onset."""
    w = w.strip().lower(); i = 0; out = []; cur = []
    while i < len(w):
        v = next((v for v in SKT_V if w.startswith(v, i)), None)
        if v:
            out.append("".join(cur)); cur = []; i += len(v); continue
        c = next((c for c in SKT_C if w.startswith(c, i)), None)
        if c: cur.append(c); i += len(c)
        else: i += 1
    return out

# ------------------------------------------------------- Later Han initials
LH_C = ['tsʰ','tśʰ','dź','tś','ts','dz','kʰ','pʰ','tʰ','ṭʰ','ḍ','ṭ','ṇ','ṣ','ś','ź',
        'ŋ','ɦ','ʔ','x','γ','k','g','p','b','m','t','d','n','s','z','h','j','w','l','r','f','v']
def lh_initial(r):
    r = r.strip()
    for c in LH_C:
        if r.startswith(c): return c
    return ""

# place/manner equivalence between Later Han and Sanskrit
GROUPS = [
    ({'p','pʰ','b','m','f','v'},               {'p','ph','b','bh','m'}),
    ({'t','tʰ','d','n','ṭ','ṭʰ','ḍ','ṇ','l'},  {'t','th','d','dh','ṭ','ṭh','ḍ','ḍh','n','ṇ'}),
    ({'k','kʰ','g','ŋ','x','γ','h','ɦ'},       {'k','kh','g','gh','ṅ','h'}),
    ({'ts','tsʰ','dz','tś','tśʰ','dź','s','z','ś','ź','ṣ'},
                                               {'c','ch','j','jh','ñ','s','ś','ṣ','y'}),
    ({'l','r','n'},                            {'l','r'}),
    ({'j','ʔ','ɦ','h','w','v'},                {'y','v','h',''}),
    ({'ʔ','ɦ','h','j','w',''},                 {''}),
]
def compatible(lh, onset):
    o = onset
    if o and o[0] in ('ṃ','ḥ'): o = o[1:]
    if lh == o: return True
    for L, S in GROUPS:
        if lh in L and o in S: return True
    if len(o) > 1:                       # Chinese renders one member of a cluster
        for part in (o[:1], o[-1:], o[:2]):
            for L, S in GROUPS:
                if lh in L and part in S: return True
    return False

# ------------------------------------------------------------------- inputs
def load_lhan():
    p = os.path.join(EXT, "LHantab.tsv")
    if not os.path.exists(p):
        log("FATAL: LHantab.tsv not found in data/external/"); sys.exit(1)
    rows = list(csv.reader(open(p, encoding="utf-8"), delimiter="\t"))
    hdr = rows[0]
    zi = hdr.index("zi") if "zi" in hdr else 1
    sy = hdr.index("syl_bok") if "syl_bok" in hdr else len(hdr) - 2
    d = defaultdict(list)
    for r in rows[1:]:
        if len(r) > max(zi, sy) and len(r[zi]) == 1 and r[sy]:
            d[r[zi]].append(r[sy])
    log(f"  LHantab.tsv: {len(d)} characters with Later Han readings")
    return d

def load_variants():
    p = os.path.join(EXT, "Unihan.zip")
    eq = defaultdict(set)
    if not os.path.exists(p):
        log("  !! Unihan.zip not found - variant fallback disabled"); return eq
    F = {"kSemanticVariant","kZVariant","kSimplifiedVariant","kTraditionalVariant"}
    with zipfile.ZipFile(p) as z:
        n = next((x for x in z.namelist() if x.endswith("Unihan_Variants.txt")), None)
        if not n: return eq
        for raw in z.open(n):
            L = raw.decode("utf-8", "replace")
            if L.startswith("#") or not L.strip(): continue
            q = L.rstrip("\n").split("\t")
            if len(q) < 3 or q[1] not in F: continue
            try: a = chr(int(q[0][2:], 16))
            except Exception: continue
            for t in re.findall(r"U\+([0-9A-Fa-f]+)", q[2]):
                b = chr(int(t, 16)); eq[a].add(b); eq[b].add(a)
    log(f"  Unihan.zip: {len(eq)} characters have a variant form")
    return eq

log("=" * 64)
log(" STEP 1 - build the transcription training set")
log("=" * 64)
log()
log("Loading phonology:")
LHAN = load_lhan(); VAR = load_variants()
def readings(c):
    if c in LHAN: return LHAN[c]
    for v in VAR.get(c, ()):
        if v in LHAN: return LHAN[v]
    return []
log()

def load_nti(fname):
    p = os.path.join(EXT, fname)
    if not os.path.exists(p):
        log(f"  !! {fname}: NOT FOUND"); return []
    out = []
    for line in open(p, encoding="utf-8"):
        if line.startswith("#"): continue
        r = line.rstrip("\n").split("\t")
        if len(r) >= 15: out.append(r)
    log(f"  {fname}: {len(out)} entries")
    return out

log("Loading NTI dictionary:")
rows = load_nti("buddhist_terminology.txt") + load_nti("buddhist_named_entities.txt")
if not rows:
    log("\nFATAL: no NTI data in data/external/."); sys.exit(1)
log(f"  total: {len(rows)}")
log()

recs = []
for r in rows:
    simp = (r[1] or "").strip()
    trad = (r[2] or "").strip()
    if trad in ("", "\\N"): trad = simp
    m = SKT.search(r[14] or "")
    if not m: continue
    skt = m.group(1)
    for cut in ("，", ",", ";", " Pali", " Pāli", " Skt", " Tibetan", " Chinese"):
        i = skt.find(cut)
        if i > 0: skt = skt[:i]
    skt = skt.strip().strip(".'\" ")
    chars = CJK.findall(trad)
    if not chars or not skt or len(skt.split()) > 2: continue
    ons = skt_onsets(skt)
    if not ons: continue
    recs.append({"trad": trad, "simp": simp, "skt": skt, "chars": chars,
                 "pos": (r[5] or "").strip(), "n_chars": len(chars), "n_syl": len(ons),
                 "onsets": ons})
log(f"Entries carrying a Sanskrit form: {len(recs)}")
seed = [r for r in recs if r["pos"] == "phonetic"]
log(f"Entries the dictionary itself tags POS='phonetic': {len(seed)}")
log()

# ------------------------------------------------------------- verify
def verify(r, shift=0):
    """Fraction of aligned positions whose Later Han initial fits the Sanskrit onset."""
    ch, on = r["chars"], r["onsets"]
    if shift > 0: on = on[shift:]
    elif shift < 0: ch = ch[-shift:]
    n = min(len(ch), len(on))
    if n == 0: return 0.0, 0
    ok = 0
    for c, o in zip(ch[:n], on[:n]):
        rs = readings(c)
        if rs and any(compatible(lh_initial(x), o) for x in rs): ok += 1
    return ok / n, n

for r in recs:
    d = r["n_chars"] - r["n_syl"]
    if d == 0:
        sc, n = verify(r); r["align"] = "exact"
    elif abs(d) == 1:
        cand = [verify(r, s) for s in (0, 1, -1)]
        sc, n = max(cand, key=lambda t: (t[0], t[1])); r["align"] = "off_by_one"
    else:
        sc, n = 0.0, 0; r["align"] = "length_mismatch"
    r["phon_score"] = round(sc, 3)
    r["n_aligned"]  = n
    r["char_syl_ratio"] = round(r["n_chars"] / r["n_syl"], 3)

# ------------------------------------------------------------- classify
# A high score over one or two aligned positions is meaningless - short calques
# match by coincidence (生死 = samsara scores 1.0 on two positions, but it is
# "birth-death", a pure calque). Demand enough positions to make the score mean
# something, and trust single characters only where the dictionary tagged them.
trans, ambig, calque = [], [], []
for r in recs:
    n = r["n_aligned"]
    single_ok = (r["n_chars"] == 1 and r["pos"] == "phonetic")
    if single_ok:
        r["label"] = "transcription"; trans.append(r); continue
    if r["align"] == "exact" and n >= 3 and r["phon_score"] >= 0.75:
        r["label"] = "transcription"; trans.append(r)
    elif r["align"] == "off_by_one" and n >= 3 and r["phon_score"] >= 0.85:
        r["label"] = "transcription"; trans.append(r)
    elif n >= 2 and r["phon_score"] >= 0.60:
        r["label"] = "ambiguous"; ambig.append(r)
    else:
        r["label"] = "calque"; calque.append(r)

log("-" * 64)
log(" Classification (phonetic verification against Later Han)")
log("-" * 64)
log(f"  transcription (音譯) : {len(trans):6d}   <-- TRAINING SET")
log(f"  ambiguous            : {len(ambig):6d}   <-- manual review")
log(f"  calque        (意譯) : {len(calque):6d}   <-- excluded")
log()
rec = sum(1 for r in seed if r["label"] == "transcription")
log(f"Recall on the dictionary's own {len(seed)} 'phonetic' entries: "
    f"{rec} ({100*rec/max(1,len(seed)):.1f}%)")
byal = Counter(r["align"] for r in trans)
log(f"Alignment of the training set: {dict(byal)}")
log()

# ------------------------------------------------------- aksara table
aks = defaultdict(Counter)
for r in trans:
    if r["align"] != "exact": continue
    for c, o in zip(r["chars"], r["onsets"]):
        aks[o][c] += 1
log(f"Aksara table induced from the training set: {len(aks)} onsets, "
    f"{sum(len(v) for v in aks.values())} character-onset pairs")
for o, v in sorted(aks.items(), key=lambda x: -sum(x[1].values()))[:6]:
    log(f"    {o or '(vowel)':8s} <- {' '.join(c for c, _ in v.most_common(10))}")
log()

# ------------------------------------------------------------- write out
COLS = ["trad","simp","skt","n_chars","n_syl","n_aligned","char_syl_ratio","phon_score","align","pos","label"]
def dump(fn, rs):
    with open(os.path.join(OUT, fn), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader(); w.writerows(rs)
dump("nti_transcription_pairs.csv", sorted(trans, key=lambda r: -r["phon_score"]))
dump("nti_ambiguous.csv",           sorted(ambig, key=lambda r: -r["phon_score"]))
dump("nti_calques_excluded.csv",    calque)
with open(os.path.join(OUT, "aksara_table.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["sanskrit_onset","chinese_char","count"])
    for o in sorted(aks):
        for c, n in aks[o].most_common(): w.writerow([o, c, n])

log("Written to data/derived/:")
log(f"  nti_transcription_pairs.csv   {len(trans)} rows  <-- the training set")
log(f"  nti_ambiguous.csv             {len(ambig)} rows")
log(f"  nti_calques_excluded.csv      {len(calque)} rows")
log(f"  aksara_table.csv              {sum(len(v) for v in aks.values())} mappings")
log()
log("NEXT: skim nti_ambiguous.csv (sorted best-first). The cut is phon_score>=0.75")
log("for exact alignments; raise it for higher precision, lower it for more data.")

with open(os.path.join(REP, "step1_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")
print("\nSummary written to reports/step1_summary.txt")
