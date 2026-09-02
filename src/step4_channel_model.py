#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 4 - the transcription channel model.

Learns P(chinese_character | source_syllable) from the verified Sanskrit pairs,
by EM over monotonic alignments that allow insertion and deletion (a Chinese
scribe could add a character for a coda, or drop a syllable entirely).

Then:
  - evaluates on a held-out split and on Baley's Late Han gold set
  - tests out-of-domain on the Ming Uyghur pairs, against a random-repairing null
  - decodes the Xiongnu names into ranked candidate syllables

WHAT THIS IS NOT: a reconstruction of the Xiongnu names. This is the CHANNEL
only - P(chinese | source). A reading also needs the source-language prior
P(name | L), which is step 5. Channel output alone will happily propose
sequences no Turkic or Yeniseian word could take.

Inputs (all produced by earlier steps, in data/derived and data/external):
  nti_transcription_pairs.csv, aksara_table.csv, uyghur_chinese_pairs.csv,
  xiongnu_*_reconstructed.csv, LHantab.tsv, Baley (in Downloads)

Stdlib only.
"""
import csv, os, re, sys, math, random
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT  = os.path.join(ROOT, "data", "external")
DER  = os.path.join(ROOT, "data", "derived")
DL   = os.path.join(ROOT, "Downloads")
DATA_DIR = os.path.join(ROOT, "data")
REP  = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)

log_lines = []
def log(s=""):
    print(s); log_lines.append(s)

CJK = re.compile(r'[一-鿿㐀-䶿]')

# --------------------------------------------------------- syllabification
SKT_C = ['kh','gh','ch','jh','ṭh','ḍh','th','dh','ph','bh',
         'k','g','ṅ','c','j','ñ','ṭ','ḍ','ṇ','t','d','n','p','b','m',
         'y','r','l','v','ś','ṣ','s','h','ṃ','ḥ']
SKT_V = ['ai','au','ā','ī','ū','ṝ','ṛ','ḹ','ḷ','a','i','u','e','o']

def tokenize(w):
    w = w.strip().lower(); i = 0; out = []
    while i < len(w):
        v = next((v for v in SKT_V if w.startswith(v, i)), None)
        if v: out.append(("V", v)); i += len(v); continue
        c = next((c for c in SKT_C if w.startswith(c, i)), None)
        if c: out.append(("C", c)); i += len(c); continue
        i += 1
    return out

def syllabify(w):
    """-> list of syllable strings, maximal-onset (last C of a cluster starts the
       next syllable, the rest closes the previous one)."""
    toks = tokenize(w)
    if not any(t == "V" for t, _ in toks): return []
    sylls, onset, cur = [], [], None
    pend = []
    for t, x in toks:
        if t == "C": pend.append(x)
        else:
            if cur is None:
                onset = pend                      # word-initial cluster
            else:
                if pend:
                    cur["coda"] = "".join(pend[:-1])
                    onset = [pend[-1]]
                else:
                    onset = []
                sylls.append(cur)
            pend = []
            cur = {"onset": "".join(onset), "vowel": x, "coda": ""}
    if cur is not None:
        cur["coda"] = "".join(pend)
        sylls.append(cur)
    return [s["onset"] + s["vowel"] + s["coda"] for s in sylls]

# ------------------------------------------------------------------ loaders
def read_csv(path):
    if not os.path.exists(path): return []
    with open(path, encoding="utf-8-sig") as f: return list(csv.DictReader(f))

log("=" * 68)
log(" STEP 4 - transcription channel model")
log("=" * 68)
log()

pairs_raw = read_csv(os.path.join(DER, "nti_transcription_pairs.csv"))
if not pairs_raw:
    log("FATAL: data/derived/nti_transcription_pairs.csv missing. Run RUN-steps.bat first.")
    sys.exit(1)

data = []
for r in pairs_raw:
    chars = CJK.findall(r["trad"] or "")
    sy = syllabify(r["skt"] or "")
    if chars and sy: data.append((chars, sy))
log(f"Training pairs loaded          : {len(data)}")
log(f"Distinct characters            : {len({c for ch,_ in data for c in ch})}")
log(f"Distinct source syllables      : {len({s for _,sy in data for s in sy})}")
log()

# seed from the induced aksara table (onset-level prior)
aks = defaultdict(Counter)
for r in read_csv(os.path.join(DER, "aksara_table.csv")):
    try: aks[r["sanskrit_onset"]][r["chinese_char"]] += int(r["count"])
    except Exception: pass
log(f"Aksara prior: {len(aks)} onsets seeding the emission table")
log()

# ------------------------------------------------------------------ EM
ALL_S = sorted({s for _, sy in data for s in sy})
ALL_C = sorted({c for ch, _ in data for c in ch})
S_IDX = {s: i for i, s in enumerate(ALL_S)}

def onset_of(s):
    t = tokenize(s)
    o = []
    for k, x in t:
        if k == "C": o.append(x)
        else: break
    return "".join(o)

# P(char | syllable), initialised from the aksara prior where it applies
P = defaultdict(lambda: defaultdict(float))
for s in ALL_S:
    o = onset_of(s)
    seed = aks.get(o, {})
    tot = sum(seed.values()) + len(ALL_C) * 0.01
    for c in ALL_C:
        P[s][c] = (seed.get(c, 0) + 0.01) / tot

LOG0 = -30.0
def lp(x): return math.log(x) if x > 0 else LOG0
P_INS, P_DEL = 0.10, 0.10          # extra character / dropped syllable

def viterbi(chars, sylls):
    """Best monotonic alignment. -> (score, list of (char_i, syll_j) matches)."""
    n, m = len(chars), len(sylls)
    NEG = -1e18
    dp = [[NEG]*(m+1) for _ in range(n+1)]
    bk = [[None]*(m+1) for _ in range(n+1)]
    dp[0][0] = 0.0
    for i in range(n+1):
        for j in range(m+1):
            if dp[i][j] == NEG: continue
            if i < n and j < m:
                v = dp[i][j] + lp(P[sylls[j]][chars[i]])
                if v > dp[i+1][j+1]: dp[i+1][j+1] = v; bk[i+1][j+1] = ("M", i, j)
            if i < n:
                v = dp[i][j] + lp(P_INS)
                if v > dp[i+1][j]: dp[i+1][j] = v; bk[i+1][j] = ("I", i, j)
            if j < m:
                v = dp[i][j] + lp(P_DEL)
                if v > dp[i][j+1]: dp[i][j+1] = v; bk[i][j+1] = ("D", i, j)
    i, j, al = n, m, []
    if dp[n][m] == NEG: return NEG, []
    while (i, j) != (0, 0):
        step = bk[i][j]
        if step is None: break
        op, pi, pj = step
        if op == "M": al.append((pi, pj))
        i, j = pi, pj
    return dp[n][m], list(reversed(al))

log("Running EM:")
for it in range(1, 9):
    cnt = defaultdict(Counter); ll = 0.0; naligned = 0
    for chars, sylls in data:
        sc, al = viterbi(chars, sylls)
        if not al: continue
        ll += sc; naligned += len(al)
        for ci, sj in al: cnt[sylls[sj]][chars[ci]] += 1
    for s in ALL_S:
        o = onset_of(s)
        seed = aks.get(o, {})
        c_s = cnt.get(s, Counter())
        tot = sum(c_s.values()) + 0.30*sum(seed.values()) + len(ALL_C)*0.01
        for c in ALL_C:
            P[s][c] = (c_s.get(c, 0) + 0.30*seed.get(c, 0) + 0.01) / tot
    log(f"  iter {it}: log-likelihood {ll:12.1f}   aligned positions {naligned}")
log()

# invert to P(syllable | char) with a uniform syllable prior
Q = defaultdict(dict)
for c in ALL_C:
    tot = sum(P[s][c] for s in ALL_S)
    for s in ALL_S:
        if tot > 0: Q[c][s] = P[s][c] / tot
# ------------------------------------------------- OOV backoff via Later Han
# Many Xiongnu characters never appear in a Buddhist transcription, so the
# character-keyed table has nothing for them. Backing off to the character's
# Later Han reading and matching its INITIAL to Sanskrit onsets keeps them
# decodable. Onsets are the part of a Chinese syllable that survives; this is
# the same assumption the transfer test rests on.
def load_lhan():
    pth = os.path.join(EXT, "LHantab.tsv")
    if not os.path.exists(pth): return {}
    rows = list(csv.reader(open(pth, encoding="utf-8"), delimiter="\t"))
    h = rows[0]
    zi = h.index("zi") if "zi" in h else 1
    sy = h.index("syl_bok") if "syl_bok" in h else len(h)-2
    d = defaultdict(list)
    for r in rows[1:]:
        if len(r) > max(zi, sy) and len(r[zi]) == 1 and r[sy]: d[r[zi]].append(r[sy])
    return d
LHAN = load_lhan()

LH_SYMS = ['tsʰ','tśʰ','dź','tś','ts','dz','kʰ','pʰ','tʰ','ṭʰ','ḍ','ṭ','ṇ','ṣ','ś','ź',
           'ŋ','ɦ','ʔ','x','γ','k','g','p','b','m','t','d','n','s','z','h','j','w','l','r','f','v']
def lh_initial(x):
    x = (x or "").strip()
    for c in LH_SYMS:
        if x.startswith(c): return c
    return ""
LH2SKT = [
    ({'p','pʰ','b','f','v'},                 {'p','ph','b','bh'}),
    ({'m'},                                  {'m'}),
    ({'t','tʰ','d','ṭ','ṭʰ','ḍ'},            {'t','th','d','dh','ṭ','ṭh','ḍ','ḍh'}),
    ({'n','ṇ'},                              {'n','ṇ'}),
    ({'k','kʰ','g','x','γ'},                 {'k','kh','g','gh'}),
    ({'ŋ'},                                  {'ṅ','g','gh'}),
    ({'ts','tsʰ','dz','tś','tśʰ','dź'},      {'c','ch','j','jh','ñ'}),
    ({'s','z','ṣ','ś','ź'},                  {'s','ś','ṣ'}),
    ({'l','r'},                              {'l','r'}),
    ({'j'},                                  {'y'}),
    ({'w'},                                  {'v'}),
    ({'ʔ','ɦ','h',''},                       {'h',''}),
]
SYL_FREQ = Counter(s for _, sy in data for s in sy)
BY_ONSET = defaultdict(list)
for s in ALL_S: BY_ONSET[onset_of(s)].append(s)

def load_variants():
    import zipfile
    zp = os.path.join(EXT, "Unihan.zip"); eq = defaultdict(set)
    if not os.path.exists(zp): return eq
    F = {"kSemanticVariant","kZVariant","kSimplifiedVariant","kTraditionalVariant"}
    try:
        with zipfile.ZipFile(zp) as z:
            nm = next((x for x in z.namelist() if x.endswith("Unihan_Variants.txt")), None)
            if not nm: return eq
            for raw in z.open(nm):
                L = raw.decode("utf-8","replace")
                if L.startswith("#") or not L.strip(): continue
                q = L.rstrip("\n").split("\t")
                if len(q) < 3 or q[1] not in F: continue
                try: a = chr(int(q[0][2:],16))
                except Exception: continue
                for t in re.findall(r"U\+([0-9A-Fa-f]+)", q[2]):
                    b = chr(int(t,16)); eq[a].add(b); eq[b].add(a)
    except Exception:
        return defaultdict(set)
    return eq
VAR = load_variants()
def lhan_readings(c):
    if c in LHAN: return LHAN[c]
    for v in VAR.get(c, ()):
        if v in LHAN: return LHAN[v]
    return []

def backoff(c, k=5):
    rs = lhan_readings(c)
    if not rs: return []
    init = lh_initial(rs[0])
    targets = set()
    for L, S in LH2SKT:
        if init in L: targets |= S
    cands = Counter()
    for o in targets:
        for s in BY_ONSET.get(o, []): cands[s] += SYL_FREQ[s]
    tot = sum(cands.values())
    if not tot: return []
    return [(s, n/tot) for s, n in cands.most_common(k)]

OOV_HITS = Counter()
def topk(c, k=5):
    if c in Q:
        return sorted(Q[c].items(), key=lambda x: -x[1])[:k]
    b = backoff(c, k)
    OOV_HITS["backoff" if b else "unresolved"] += 1
    return b

# ------------------------------------------------------------- evaluation
log("-" * 68)
log(" Evaluation")
log("-" * 68)
random.seed(17)
idx = list(range(len(data))); random.shuffle(idx)
cut = int(0.8*len(idx)); test = [data[i] for i in idx[cut:]]

def evaluate(pairs, name):
    t1 = t3 = o1 = n = 0
    for chars, sylls in pairs:
        _, al = viterbi(chars, sylls)
        for ci, sj in al:
            c, gold = chars[ci], sylls[sj]
            cand = topk(c, 3)
            if not cand: continue
            n += 1
            names = [s for s, _ in cand]
            if names and names[0] == gold: t1 += 1
            if gold in names: t3 += 1
            if names and onset_of(names[0]) == onset_of(gold): o1 += 1
    if n == 0:
        log(f"  {name}: no scoreable positions"); return
    log(f"  {name}  (n={n} positions)")
    log(f"      exact syllable  top-1 {100*t1/n:5.1f}%   top-3 {100*t3/n:5.1f}%")
    log(f"      onset only      top-1 {100*o1/n:5.1f}%")

evaluate(test, "held-out 20% of the Sanskrit pairs")

# Baley - independent Late Han gold set, never trained on (TAB-separated!)
bal = []
bp = os.path.join(DL, "baley_late_han_v7.csv")
if os.path.exists(bp):
    with open(bp, encoding="utf-8-sig") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    hdr = rows[0]
    try:
        ci = hdr.index("Chinese"); si = hdr.index("Sanskrit")
    except ValueError:
        ci = si = None
    if ci is not None:
        for r in rows[1:]:
            if len(r) <= max(ci, si): continue
            chars = CJK.findall(r[ci] or "")
            sy = syllabify((r[si] or "").strip())
            if chars and sy: bal.append((chars, sy))
    log()
    log(f"  Baley Late Han gold set: {len(bal)} usable pairs (of 409 rows)")
    if bal: evaluate(bal, "Baley Late Han (independent, never trained on)")
else:
    log("\n  Baley file not found in Downloads - skipped")

# ------------------------------------------------- out-of-domain: Uyghur
log()
log("-" * 68)
log(" Out-of-domain: does the channel predict TURKIC onsets?")
log("-" * 68)
TUR_V = set("aeiouäöüïıəɨ")
def tur_onsets(w):
    w = w.strip().lower(); out=[]; cur=[]
    for ch in w:
        if ch in TUR_V: out.append("".join(cur)); cur=[]
        elif ch.isalpha() or ch in "ɣŋčšžǰḳ": cur.append(ch)
        else: cur=[]
    return out
EQ = [({'p','ph','b','bh'},{'p','b'}), ({'m'},{'m'}),
      ({'t','th','d','dh','ṭ','ṭh','ḍ','ḍh'},{'t','d'}), ({'n','ṇ'},{'n'}),
      ({'k','kh','g','gh'},{'k','g','q','ɣ','x'}), ({'ṅ'},{'ŋ'}),
      ({'s','ś','ṣ'},{'s','š','z','ž'}), ({'c','ch','j','jh','ñ'},{'č','ǰ','c','j'}),
      ({'l'},{'l','r'}), ({'r'},{'r','l'}), ({'y'},{'y'}), ({'v'},{'v','w'}),
      ({'h',''},{'h',''})]
def ok(skt_onset, tur_onset):
    if skt_onset == tur_onset: return True
    for A,B in EQ:
        if skt_onset in A and tur_onset in B: return True
    if len(tur_onset) > 1:
        for part in (tur_onset[:1], tur_onset[-1:]):
            for A,B in EQ:
                if skt_onset in A and part in B: return True
    return False

uy = []
for r in read_csv(os.path.join(DER, "uyghur_chinese_pairs.csv")):
    ch = CJK.findall(r["chinese"] or "")
    w  = (r["uyghur_variants"] or "").split("|")[-1].strip()
    o  = tur_onsets(w)
    if ch and o: uy.append((ch, o))
if not uy:
    log("  no Uyghur pairs found - run RUN-uyghur.bat first")
else:
    def uy_score(items):
        hit = n = 0
        for ch, ons in items:
            for c, o in zip(ch, ons):
                cand = topk(c, 1)
                if not cand: continue
                n += 1
                if ok(onset_of(cand[0][0]), o): hit += 1
        return (hit/n if n else 0.0), n
    real, n = uy_score(uy)
    pool = defaultdict(list)
    for ch, o in uy: pool[len(o)].append(o)
    perms = []
    for _ in range(200):
        shuffled = []
        for ch, o in uy:
            cands = pool[len(o)]
            shuffled.append((ch, random.choice(cands) if len(cands) > 1 else o))
        perms.append(uy_score(shuffled)[0])
    mp = sum(perms)/len(perms)
    beat = sum(1 for x in perms if x >= real)
    log(f"  pairs {len(uy)}, positions scored {n}")
    log(f"  channel top-1 onset predicts Turkic : {real:.3f}")
    log(f"  random re-pairing null              : {mp:.3f}")
    log(f"  lift                                : {real-mp:+.3f}   "
        f"p={(beat+1)/(len(perms)+1):.4f}")
    log()
    if real - mp >= 0.15:
        log("  The channel - trained only on Sanskrit - carries to Turkic.")
    else:
        log("  Weak or no carry-over. The channel is over-fitted to Sanskrit.")

# ------------------------------------------------- decode the Xiongnu names
log()
log("-" * 68)
log(" Xiongnu names through the channel (NO source-language prior yet)")
log("-" * 68)
OOV_HITS.clear()          # count only the Xiongnu decode below
rows = (read_csv(os.path.join(DER, "xiongnu_rulers_reconstructed.csv")) +
        read_csv(os.path.join(DER, "xiongnu_titles_lexicon_reconstructed.csv")))
out = []
for r in rows:
    chars = CJK.findall(r.get("chinese") or "")
    if not chars: continue
    cells, best, srcs = [], [], []
    for c in chars:
        direct = c in Q
        t = topk(c, 3)
        if t:
            tag = "" if direct else "*"
            cells.append(f"{c}{tag}:" + ",".join(f"{s}({p:.2f})" for s, p in t))
            best.append(t[0][0] + tag)
            srcs.append("direct" if direct else "lhan_backoff")
        else:
            cells.append(f"{c}:UNRESOLVED"); best.append("?"); srcs.append("none")
    out.append({"chinese": r.get("chinese",""), "pinyin": r.get("pinyin_modern",""),
                "entry_type": r.get("entry_type",""),
                "channel_top1": " ".join(best),
                "path": ",".join(srcs),
                "proposed_reading": r.get("proposed_reading",""),
                "candidates": " | ".join(cells)})
WANT = ["撑犁","孤塗","單于","屠耆","頭曼","冒頓","攣鞮","匈奴","羯"]
for o in out:
    if o["chinese"] in WANT:
        pr = f"   [lit: {o['proposed_reading']}]" if o["proposed_reading"] else ""
        log(f"  {o['chinese']:6s} -> {o['channel_top1']:<28s}{pr}")
with open(os.path.join(DER, "xiongnu_channel_candidates.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["chinese","pinyin","entry_type","channel_top1",
                                      "path","proposed_reading","candidates"])
    w.writeheader(); w.writerows(out)
log()
log(f"  * marks a character decoded via the Later Han backoff, not seen directly")
log(f"    in Buddhist transcriptions. backoff used: {OOV_HITS['backoff']}, "
    f"still unresolved: {OOV_HITS['unresolved']}")
log()
log("  !! These are CHANNEL-ONLY outputs. The channel asks 'what source syllable")
log("  most often produced this character?' - trained on Sanskrit. It has no idea")
log("  what a Turkic or Yeniseian word may look like. Sanskrit-shaped output here")
log("  is expected and is NOT a reconstruction. Adding P(name | language) is what")
log("  turns this into evidence, and that is step 5.")

# Emit candidates for every character any later step will ask about - the
# training characters PLUS the Xiongnu names and the Uyghur pairs. Without the
# backoff characters here, step 5 cannot score most names at all.
need = set(ALL_C)
for r in rows:
    need.update(CJK.findall(r.get("chinese") or ""))
for r in read_csv(os.path.join(DER, "uyghur_chinese_pairs.csv")):
    need.update(CJK.findall(r.get("chinese") or ""))
for r in read_csv(os.path.join(DATA_DIR, "control_sets.csv")):
    need.update(CJK.findall(r.get("chinese") or ""))
if bal:
    for chars, _ in bal: need.update(chars)

wrote = Counter()
with open(os.path.join(DER, "channel_emissions.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["chinese_char","source_syllable","p_syllable_given_char","path"])
    for c in sorted(need):
        direct = c in Q
        for s, p in topk(c, 5):
            if p >= 0.005:
                w.writerow([c, s, round(p, 4), "direct" if direct else "lhan_backoff"])
                wrote["direct" if direct else "lhan_backoff"] += 1
log()
log(f"Emission table covers {len(need)} characters "
    f"({wrote['direct']} direct rows, {wrote['lhan_backoff']} backoff rows)")

log()
log("Written to data/derived/:")
log("  channel_emissions.csv            P(syllable | character), top 5 each")
log("  xiongnu_channel_candidates.csv   ranked candidates per name")

with open(os.path.join(REP, "step4_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")
print("\nSummary written to reports/step4_summary.txt")
