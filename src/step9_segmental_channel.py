#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 9 - segmental channel trained on the Secret History corpus.

THE EXPERIMENT THIS SETTLES. Steps 5-7 failed, and the failures were consistent
with two incompatible explanations: the method is wrong, or 1,017 pairs is not
enough. This trains the same idea on 9,329 genuine Mongolian pairs (37,250
character tokens, ~70 observations per character against a handful before) with
two changes:

  1. SEGMENTAL output units, not whole Sanskrit syllables. A character maps to
     1-3 segments, so any phoneme sequence becomes producible and the Sanskrit
     inventory ceiling (only 33% of Turkic gold forms reachable) disappears.
  2. Enough data per character for the character-keyed table to be estimable.

Reports the same metrics as steps 4 and 7 so the comparison is like-for-like:
per-position accuracy, whole-form top-k, and edit distance to gold.

If per-position accuracy climbs well above the 46.4% the Sanskrit-trained channel
managed, the approach is sound and the earlier failures were about data. If it
does not, the approach is wrong - and that is worth knowing before any rewrite.

Stdlib only. Needs data/derived/shm_transcription_pairs.csv from step 8.
"""
import csv, math, os, random, re, sys
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DER  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)
out = []
def log(s=""):
    print(s); out.append(s)

CJK = re.compile(r'[㐀-䶿一-鿿]')

# --------------------------------------------------- Mongolian segmentation
# The edition's romanisation uses c-caron, n-dot-above, gamma(+dot), z-caron,
# s-caron, front-rounded vowels, and a combining dot above. Normalise to single
# tokens so alignment operates on real segments.
COMBINING_DOT = "̇"
MULTI = [("γ"+COMBINING_DOT, "G"), ("g"+COMBINING_DOT, "G"),
         ("n"+COMBINING_DOT, "N"), ("ṅ", "N"), ("γ", "G"), ("ġ", "G"),
         ("č", "C"), ("ž", "J"), ("š", "S"), ("ḳ", "q"), ("ǰ", "J")]
VOWELS = set("aeiouäöüïıə")
def segs(w):
    """Romanised Mongolian -> list of segment tokens."""
    s = (w or "").strip()
    for a, b in MULTI: s = s.replace(a, b)
    s = s.replace("-", " ").replace("(", "").replace(")", "")
    s = re.sub(r'[^A-Za-zäöüïıə ]', '', s)
    out_ = []
    for ch in s:
        if ch == " ": continue
        out_.append(ch)
    return out_
def is_v(x): return x.lower() in VOWELS

log("=" * 70)
log(" STEP 9 - segmental channel on the Secret History corpus")
log("=" * 70)
log()
p = os.path.join(DER, "shm_transcription_pairs.csv")
if not os.path.exists(p):
    log("FATAL: data/derived/shm_transcription_pairs.csv missing. Run step 8 first.")
    sys.exit(1)
rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
data = []
for r in rows:
    ch = CJK.findall(r["chinese"] or "")
    sg = segs(r["mongolian"])
    if len(ch) >= 1 and len(sg) >= 2 and len(sg) <= 4*len(ch) + 3:
        data.append((ch, sg))
log(f"pairs usable                 : {len(data):,} of {len(rows):,}")
chars = Counter(c for ch, _ in data for c in ch)
log(f"character tokens             : {sum(chars.values()):,}")
log(f"distinct characters          : {len(chars):,}")
log(f"mean observations / character : {sum(chars.values())/len(chars):.1f}")
log(f"characters with >=20 obs      : {sum(1 for v in chars.values() if v>=20)}")
log()

# ------------------------------------------------------------------- EM
MAXCH = 3                        # a character may cover 1-3 segments
def chunks_at(sg, j):
    return [tuple(sg[j:j+L]) for L in range(1, MAXCH+1) if j+L <= len(sg)]

# A RANDOM split leaks: held-out items come from the same chapters, sharing
# names and formulae with training. Holding out whole DOCUMENTS instead tests
# generalisation to unseen text, which is the number that matters and the only
# one comparable to the cross-corpus figures from steps 4 and 7.
by_doc = defaultdict(list)
for r in rows:
    ch = CJK.findall(r["chinese"] or ""); sg = segs(r["mongolian"])
    if len(ch) >= 1 and len(sg) >= 2 and len(sg) <= 4*len(ch) + 3:
        by_doc[r.get("source_doc","?")].append((ch, sg))
doclist = sorted(by_doc, key=lambda d: -len(by_doc[d]))
random.seed(19)
random.shuffle(doclist)
hold = set()
target = 0.15*sum(len(v) for v in by_doc.values())
acc_n = 0
for d in doclist:
    if acc_n >= target: break
    hold.add(d); acc_n += len(by_doc[d])
train = [x for d, v in by_doc.items() if d not in hold for x in v]
test  = [x for d in hold for x in by_doc[d]]
log(f"split by DOCUMENT: {len(train):,} train / {len(test):,} held out")
log(f"  {len(by_doc)-len(hold)} training documents, {len(hold)} held-out documents")
log("  (held-out text is from chapters the model never saw - no shared formulae)")
log()

ALLC = sorted(chars)
P = defaultdict(lambda: defaultdict(float))     # P[char][chunk]
# uniform-ish init over the chunks actually observed anywhere
seen_chunks = Counter()
for ch, sg in train:
    for j in range(len(sg)):
        for k in chunks_at(sg, j): seen_chunks[k] += 1
CH_LIST = [k for k, n in seen_chunks.items() if n >= 2]
log(f"candidate segment chunks (seen >=2x): {len(CH_LIST):,}")
CHSET = set(CH_LIST)
for c in ALLC:
    for k in CH_LIST: P[c][k] = 1.0/len(CH_LIST)

LOG0 = -30.0
def lp(x): return math.log(x) if x > 0 else LOG0
P_SKIP = 0.02        # character covering no segment (rare)

def align(ch, sg, tbl):
    """Viterbi: each character covers 1-3 consecutive segments (or is skipped)."""
    n, m = len(ch), len(sg)
    NEG = -1e18
    dp = [[NEG]*(m+1) for _ in range(n+1)]
    bk = [[None]*(m+1) for _ in range(n+1)]
    dp[0][0] = 0.0
    for i in range(n):
        for j in range(m+1):
            if dp[i][j] == NEG: continue
            for L in range(1, MAXCH+1):
                if j+L > m: break
                k = tuple(sg[j:j+L])
                v = dp[i][j] + lp(tbl[ch[i]].get(k, 0.0))
                if v > dp[i+1][j+L]:
                    dp[i+1][j+L] = v; bk[i+1][j+L] = (i, j, k)
            v = dp[i][j] + lp(P_SKIP)
            if v > dp[i+1][j]:
                dp[i+1][j] = v; bk[i+1][j] = (i, j, None)
    if dp[n][m] == NEG: return NEG, []
    i, j, al = n, m, []
    while (i, j) != (0, 0):
        st = bk[i][j]
        if st is None: break
        pi, pj, k = st
        if k is not None: al.append((pi, k))
        i, j = pi, pj
    return dp[n][m], list(reversed(al))

log("Running EM:")
for it in range(1, 11):
    cnt = defaultdict(Counter); ll = 0.0; na = 0
    for ch, sg in train:
        sc, al = align(ch, sg, P)
        if not al: continue
        ll += sc; na += len(al)
        for ci, k in al: cnt[ch[ci]][k] += 1
    for c in ALLC:
        cc = cnt.get(c, Counter())
        tot = sum(cc.values()) + 0.02*len(CH_LIST)
        d = P[c]; d.clear()
        for k, v in cc.items(): d[k] = (v + 0.02)/tot
        d.default_factory = lambda: 0.02/tot if tot else 0.0
        d["__floor__"] = 0.0
    log(f"  iter {it:2d}: log-likelihood {ll:12.1f}  aligned {na:,}")
log()

def topk_chunk(c, k=5):
    d = P.get(c)
    if not d: return []
    items = [(kk, v) for kk, v in d.items() if kk != "__floor__" and v > 0]
    items.sort(key=lambda x: -x[1])
    return items[:k]

# ------------------------------------------------------------ evaluation
log("-" * 70)
log(" PER-POSITION ACCURACY  (compare: Sanskrit-trained channel was 46.4%)")
log("-" * 70)
t1 = t3 = o1 = n = 0
for ch, sg in test:
    _, al = align(ch, sg, P)
    for ci, gold in al:
        cand = topk_chunk(ch[ci], 3)
        if not cand: continue
        n += 1
        names = [k for k, _ in cand]
        if names[0] == gold: t1 += 1
        if gold in names: t3 += 1
        if names[0] and gold and names[0][0] == gold[0]: o1 += 1
if n:
    log(f"  positions scored : {n:,}")
    log(f"  exact chunk       top-1 {100*t1/n:5.1f}%   top-3 {100*t3/n:5.1f}%")
    log(f"  first segment     top-1 {100*o1/n:5.1f}%   "
        f"(compare: Sanskrit channel onset 79.6%)")
log()

# ------------------------------------------------- whole-form reconstruction
BEAM, TOPN, KMAX = 300, 5, 20
def decode(ch, k=KMAX):
    beams = [((), 0.0)]
    for c in ch:
        cs = topk_chunk(c, TOPN)
        if not cs: return []
        nxt = []
        for pre, s in beams:
            for kk, pv in cs:
                nxt.append((pre + kk, s + math.log(pv)))
        nxt.sort(key=lambda t: -t[1]); beams = nxt[:BEAM]
    best = {}
    for w, s in beams:
        t = "".join(w)
        if t not in best or s > best[t]: best[t] = s
    items = sorted(best.items(), key=lambda kv: -kv[1])[:k]
    m = max(s for _, s in items)
    tot = sum(math.exp(s-m) for _, s in items)
    return [(w, math.exp(s-m)/tot) for w, s in items]

def editdist(a, b):
    if a == b: return 0
    prev = list(range(len(b)+1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j]+1, cur[j-1]+1, prev[j-1]+(ca != cb)))
        prev = cur
    return prev[-1]

log("-" * 70)
log(" WHOLE-FORM RECONSTRUCTION on held-out data")
log(" (compare: Sanskrit channel on Baley - exact 8.2%, within-1 17.4%,")
log("  within-2 32.8%, mean normalised edit distance 0.410)")
log("-" * 70)
random.seed(3)
sample = test if len(test) <= 400 else random.sample(test, 400)
KS = (1, 3, 5, 10, 20)
hit = {k: 0 for k in KS}; ex = e1 = e2 = m = 0; tot = 0.0
for ch, sg in sample:
    got = decode(ch)
    if not got: continue
    m += 1
    gold = "".join(sg)
    forms = [w for w, _ in got]
    for k in KS:
        if gold in forms[:k]: hit[k] += 1
    d = min(editdist(w, gold) for w in forms)
    ex += (d == 0); e1 += (d <= 1); e2 += (d <= 2); tot += d/max(len(gold), 1)
if m:
    log(f"  forms scored : {m}")
    for k in KS: log(f"      top-{k:<3d} exact {100*hit[k]/m:5.1f}%")
    log(f"  best-of-top-20: exact {100*ex/m:5.1f}%   within 1 {100*e1/m:5.1f}%   "
        f"within 2 {100*e2/m:5.1f}%")
    log(f"  mean normalised edit distance: {tot/m:.3f}")
log()

log("SAMPLE - held-out reconstructions (gold vs top candidate):")
for ch, sg in sample[:12]:
    got = decode(ch, 3)
    if not got: continue
    gold = "".join(sg)
    mark = "OK " if got[0][0] == gold else "   "
    log(f"  {mark}{''.join(ch):10s} gold={gold:16s} -> " +
        ", ".join(f"{w}({p:.2f})" for w, p in got))
log()

with open(os.path.join(DER, "shm_channel_emissions.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["chinese_char","segments","p"])
    for c in ALLC:
        for k, v in topk_chunk(c, 6):
            if v >= 0.01: w.writerow([c, "".join(k), round(v, 4)])
log("Written to data/derived/shm_channel_emissions.csv")
with open(os.path.join(REP, "step9_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\nSummary written to reports/step9_summary.txt")
