#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 7 - reconstruct pronunciations, ranked, with probabilities.

The pivot away from language attribution (step 6 showed that is not supportable
on available data). Instead of asking "which language is this?", produce the
candidate source forms consistent with the transcription and let the reader
judge affiliation.

Two things make this defensible where attribution was not:

1. A LANGUAGE-NEUTRAL prior. Not Turkic, not Yeniseian - a universal phonotactic
   model fitted on a typologically balanced sample drawn from every family in
   ASJP. It answers "is this a plausible word in SOME human language?", which
   regularises the output without taking a position on affiliation.

2. IT IS EVALUABLE. There is ground truth for pronunciation - Baley's Late Han
   Sanskrit pairs and the Ming Uyghur pairs - so top-k accuracy is measurable.
   There is no ground truth for Xiongnu affiliation and never will be.

Also reports the REACHABILITY CEILING: the channel's syllable inventory comes
from Sanskrit, so forms needing segments Sanskrit lacks (Turkic q-, front-rounded
vowels) cannot be produced at all, however good the search. That bound is
reported rather than hidden.

Stdlib only. Needs step 4's channel_emissions.csv and asjp-v19.1.zip.
"""
import csv, io, math, os, random, re, sys, zipfile
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DER  = os.path.join(ROOT, "data", "derived")
DL   = os.path.join(ROOT, "Downloads")
REP  = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)
log_lines = []
def log(s=""):
    print(s); log_lines.append(s)
CJK = re.compile(r'[一-鿿㐀-䶿]')
def rc(p):
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8-sig") as f: return list(csv.DictReader(f))

ASJP_OK = set("pbfvmw84tdsznrlSZCjT5ykgxNqGX7hL" + "ieE3auo")
V = set("ieE3auo")
def clean(f): return "".join(c for c in (f or "") if c in ASJP_OK)
def nvow(w): return sum(1 for c in w if c in V)

SKT2 = [('kh','k'),('gh','g'),('ch','C'),('jh','j'),('ṭh','t'),('ḍh','d'),('th','t'),
 ('dh','d'),('ph','p'),('bh','b'),('ai','aj'),('au','aw'),('ā','a'),('ī','i'),('ū','u'),
 ('ṝ','r'),('ṛ','r'),('ḹ','l'),('ḷ','l'),('ṅ','N'),('ñ','5'),('ṭ','t'),('ḍ','d'),
 ('ṇ','n'),('ś','S'),('ṣ','S'),('ṃ','N'),('ḥ','h'),('c','C'),('j','j'),('k','k'),
 ('g','g'),('t','t'),('d','d'),('n','n'),('p','p'),('b','b'),('m','m'),('y','y'),
 ('r','r'),('l','l'),('v','v'),('s','s'),('h','h'),('a','a'),('i','i'),('u','u'),
 ('e','e'),('o','o')]
def to_asjp(s):
    s=(s or "").strip().lower(); o=[]; i=0
    while i<len(s):
        for a,b in SKT2:
            if s.startswith(a,i): o.append(b); i+=len(a); break
        else: i+=1
    return "".join(o)
UYM = {"č":"C","š":"S","ž":"Z","ǰ":"j","ŋ":"N","ɣ":"G","ä":"E","ö":"o","ü":"u",
       "ï":"3","ı":"3","ə":"3","c":"C"}
def uy_asjp(w):
    w = "".join(c for c in (w or "").lower() if c.isalpha() or c in "ɣŋčšžǰ")
    return clean("".join(UYM.get(c,c) for c in w))

log("=" * 70)
log(" STEP 7 - ranked pronunciation reconstruction")
log("=" * 70)
log()

# ------------------------------------------------ language-neutral prior
ZP = os.path.join(DL, "asjp-v19.1.zip")
if not os.path.exists(ZP): log(f"FATAL: {ZP} not found."); sys.exit(1)
with zipfile.ZipFile(ZP) as z:
    base = next(n for n in z.namelist() if n.endswith("cldf/languages.csv")).rsplit("/",1)[0]+"/"
    langs = {}
    with z.open(base+"languages.csv") as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8")): langs[r["ID"]] = r
    byl = defaultdict(list)
    with z.open(base+"forms.csv") as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8")):
            c = clean(r["Form"])
            if c: byl[r["Language_ID"]].append(c)

# typologically balanced: cap the contribution of any single doculect, and of any
# single family, so the prior is not dominated by well-sampled regions.
random.seed(31)
PER_LANG, PER_FAM = 12, 1200
fam_of = {k: (langs[k].get("Family") or "?") for k in langs}
byfam = defaultdict(list)
for k, forms in byl.items():
    if not forms: continue
    take = forms if len(forms) <= PER_LANG else random.sample(forms, PER_LANG)
    byfam[fam_of.get(k, "?")].extend(take)
neutral = []
for fm, forms in byfam.items():
    neutral.extend(forms if len(forms) <= PER_FAM else random.sample(forms, PER_FAM))
random.shuffle(neutral)
log(f"Language-neutral prior: {len(neutral)} forms from {len(byfam)} families")
log(f"  (capped at {PER_LANG} forms per doculect and {PER_FAM} per family, so no")
log("   region or family dominates - this is 'plausible in SOME human language')")
log()

class NGram:
    def __init__(self, forms, order=4):
        self.order=order; self.cnt=[defaultdict(Counter) for _ in range(order)]; self.voc=set()
        for w in forms:
            s="^"*(order-1)+w+"$"; self.voc.update(w)
            for i in range(order-1,len(s)):
                for k in range(order): self.cnt[k][s[i-k:i]][s[i]]+=1
        self.V=max(len(self.voc),1)+1
    def logp(self, w):
        s="^"*(self.order-1)+w+"$"; t=0.0
        for i in range(self.order-1,len(s)):
            ch=s[i]; p=None
            for k in range(self.order-1,-1,-1):
                c=self.cnt[k][s[i-k:i]]; n=sum(c.values())
                if n>=4: p=(c[ch]+0.3)/(n+0.3*self.V); break
            if p is None:
                c=self.cnt[0][""]; n=sum(c.values()) or 1; p=(c[ch]+0.3)/(n+0.3*self.V)
            t+=math.log(p)
        return t
NEUTRAL = NGram(neutral)
log("Fitted a 4-gram universal phonotactic model.")
log()

# ----------------------------------------------------------- the channel
em = rc(os.path.join(DER, "channel_emissions.csv"))
if not em:
    log("FATAL: data/derived/channel_emissions.csv missing. Run step 4."); sys.exit(1)
CAND = defaultdict(list)
for r in em:
    try: CAND[r["chinese_char"]].append((r["source_syllable"], float(r["p_syllable_given_char"])))
    except Exception: pass
for c in CAND: CAND[c].sort(key=lambda x: -x[1])
INVENTORY = {s for v in CAND.values() for s, _ in v}
log(f"Channel: {len(CAND)} characters, {len(INVENTORY)} distinct source syllables")
SEGS = set()
for s in INVENTORY: SEGS.update(to_asjp(s))
log(f"Reachable segments (ASJP): {''.join(sorted(SEGS))}")
log()

# ------------------------------------------------------- top-k decoding
BEAM, TOPN, KMAX = 400, 5, 20
W_PRIOR = 1.0
def decode(chars, k=KMAX, w_prior=W_PRIOR):
    """-> [(asjp_form, normalised_probability), ...] best first."""
    beams = [("", 0.0)]
    for c in chars:
        cs = CAND.get(c, [])[:TOPN]
        if not cs: return []
        nxt = []
        for pre, lp in beams:
            for syl, p in cs:
                if p <= 0: continue
                nxt.append((pre + to_asjp(syl), lp + math.log(p)))
        nxt.sort(key=lambda t: -(t[1] + w_prior*NEUTRAL.logp(t[0])))
        beams = nxt[:BEAM]
    if not beams: return []
    scored = [(lp + w_prior*NEUTRAL.logp(w), w) for w, lp in beams]
    # merge duplicate strings, then normalise over the beam
    best = {}
    for sc, w in scored:
        if w not in best or sc > best[w]: best[w] = sc
    items = sorted(best.items(), key=lambda kv: -kv[1])[:k]
    m = max(s for _, s in items)
    tot = sum(math.exp(s - m) for _, s in items)
    return [(w, math.exp(s - m)/tot) for w, s in items]

# --------------------------------------------- reachability ceiling first
log("-" * 70)
log(" REACHABILITY CEILING - what fraction of gold forms CAN be produced?")
log("-" * 70)
log()
log(" The channel's syllable inventory is Sanskrit-derived. A gold form needing")
log(" a segment Sanskrit lacks can never be produced, however good the search.")
log(" This bounds top-k accuracy from above.")
log()
def reachable(gold):
    return bool(gold) and all(ch in SEGS for ch in gold)

uy_pairs = []
for r in rc(os.path.join(DER, "uyghur_chinese_pairs.csv")):
    ch = CJK.findall(r["chinese"] or "")
    g  = uy_asjp((r["uyghur_variants"] or "").split("|")[-1].strip())
    if ch and len(g) >= 2: uy_pairs.append((ch, g, r))
bal_pairs = []
bp = os.path.join(DL, "baley_late_han_v7.csv")
if os.path.exists(bp):
    with open(bp, encoding="utf-8-sig") as f: rows = list(csv.reader(f, delimiter="\t"))
    hdr = rows[0]
    if "Chinese" in hdr and "Sanskrit" in hdr:
        ci, si = hdr.index("Chinese"), hdr.index("Sanskrit")
        for r in rows[1:]:
            if len(r) <= max(ci, si): continue
            ch = CJK.findall(r[ci] or "")
            g  = clean(to_asjp((r[si] or "").strip()))
            if ch and len(g) >= 2: bal_pairs.append((ch, g, None))
for nm, ps in (("Ming Uyghur", uy_pairs), ("Baley Late Han Sanskrit", bal_pairs)):
    if not ps: log(f"  {nm}: none loaded"); continue
    r_ok = sum(1 for _, g, _ in ps if reachable(g))
    log(f"  {nm}: {r_ok}/{len(ps)} gold forms reachable ({100*r_ok/len(ps):.1f}%)")
    bad = Counter(ch for _, g, _ in ps for ch in g if ch not in SEGS)
    if bad: log(f"      blocking segments: " +
                "  ".join(f"{c}({n})" for c, n in bad.most_common(8)))
log()

# ------------------------------------------------------------ evaluation
log("-" * 70)
log(" TOP-K ACCURACY (exact ASJP string match against gold)")
log("-" * 70)
log()
def editdist(a, b):
    if a == b: return 0
    prev = list(range(len(b)+1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j]+1, cur[j-1]+1, prev[j-1]+(ca != cb)))
        prev = cur
    return prev[-1]

def evaluate(pairs, label, cap=200):
    if not pairs: log(f"  {label}: no data"); return
    random.seed(7)
    use = pairs if len(pairs) <= cap else random.sample(pairs, cap)
    KS = (1, 3, 5, 10, 20)
    hit = {k: 0 for k in KS}; hit_on = {k: 0 for k in KS}
    n = 0; reach = 0
    for ch, g, _ in use:
        got = decode(ch)
        if not got: continue
        n += 1
        if reachable(g): reach += 1
        forms = [w for w, _ in got]
        # onset-sequence match: consonant onsets in order, a looser standard
        def onsets(w):
            out=[]; cur=[]
            for c in w:
                if c in V: out.append("".join(cur)); cur=[]
                else: cur.append(c)
            return tuple(out)
        go = onsets(g)
        for k in KS:
            if g in forms[:k]: hit[k] += 1
            if any(onsets(w) == go for w in forms[:k]): hit_on[k] += 1
    if not n: log(f"  {label}: nothing decodable"); return
    log(f"  {label}  (n={n}, {100*reach/n:.0f}% of gold forms reachable)")
    log("      k          exact    onset-sequence")
    for k in KS:
        log(f"      top-{k:<3d}  {100*hit[k]/n:8.1f}%  {100*hit_on[k]/n:12.1f}%")
    # exact match is unforgiving - one wrong segment fails. Edit distance says
    # whether the reconstruction is at least CLOSE, which is the honest question.
    ex=e1=e2=0; tot=0.0; m2=0
    for ch, g, _ in use:
        got = decode(ch)
        if not got: continue
        m2 += 1
        d = min(editdist(w, g) for w, _ in got)
        ex += (d==0); e1 += (d<=1); e2 += (d<=2); tot += d/max(len(g),1)
    if m2:
        log(f"      best-of-top-20 edit distance to gold:")
        log(f"         exact {100*ex/m2:5.1f}%   within 1 {100*e1/m2:5.1f}%   "
            f"within 2 {100*e2/m2:5.1f}%   mean normalised {tot/m2:.3f}")
    log()
evaluate(bal_pairs, "Baley Late Han Sanskrit (independent gold)")
evaluate(uy_pairs,  "Ming Uyghur (out-of-domain gold)")

# --------------------------------------------------------------- XIONGNU
log("-" * 70)
log(" XIONGNU NAMES - ranked candidate pronunciations")
log("-" * 70)
log()
rows = (rc(os.path.join(DER, "xiongnu_rulers_reconstructed.csv")) +
        rc(os.path.join(DER, "xiongnu_titles_lexicon_reconstructed.csv")))
out = []
SHOW = ["撑犁","孤塗","單于","屠耆","頭曼","冒頓","攣鞮","虛連題","呼韓邪","匈奴","羯","閼氏"]
for r in rows:
    ch = CJK.findall(r.get("chinese") or "")
    if not ch: continue
    got = decode(ch)
    if not got: continue
    rec = {"chinese": r.get("chinese",""), "pinyin": r.get("pinyin_modern",""),
           "entry_type": r.get("entry_type",""),
           "lhan_chinese_side": r.get("lhan_schuessler",""),
           "proposed_in_literature": r.get("proposed_reading",""),
           "top1": got[0][0], "top1_p": round(got[0][1],4),
           "candidates": " | ".join(f"{w} {p:.3f}" for w, p in got[:10])}
    out.append(rec)
log(f"{'name':7s} {'ranked candidates (ASJP), best first':46s} literature")
log("-" * 70)
for rec in out:
    if rec["chinese"] not in SHOW: continue
    cands = " ".join(f"{w}({p:.2f})" for w, p in
                     [(x.split()[0], float(x.split()[1]))
                      for x in rec["candidates"].split(" | ")[:4]])
    log(f"{rec['chinese']:7s} {cands:46s} {rec['proposed_in_literature']}")
log()
with open(os.path.join(DER, "xiongnu_reconstructions.csv"), "w", newline="", encoding="utf-8-sig") as f:
    if out:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

log("HOW TO READ THIS, and what it is not:")
log("  * Forms are in ASJP notation (C=ch, S=sh, N=ng, 3=schwa, E=ae). Probabilities")
log("    are normalised over the retained beam, so they are RELATIVE rankings, not")
log("    absolute posteriors.")
log("  * The prior is language-neutral by design. It does not favour Turkic,")
log("    Yeniseian, Mongolic or anything else, and no attribution is implied.")
log("  * The syllable inventory is Sanskrit-derived, so segments Sanskrit lacks -")
log("    q, front-rounded vowels - cannot appear. See the reachability ceiling; it")
log("    caps how often the true form can be produced at all.")
log("  * Read the top-k accuracy on Baley and Uyghur as the honest measure of how")
log("    much to trust any single line above.")
log()
log("Written to data/derived/xiongnu_reconstructions.csv")
with open(os.path.join(REP, "step7_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines)+"\n")
print("\nSummary written to reports/step7_summary.txt")
