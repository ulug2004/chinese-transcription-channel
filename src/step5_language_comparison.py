#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 5 - competing-language comparison.

The channel (step 4) gives P(characters | source form). This adds the missing
half - P(form | language L) - and compares languages:

    P(chars | L) = SUM over candidate forms  P(chars | form) * P(form | L)

then reports Bayes factors between languages. Because it is a comparison, it can
return "Yeniseian", "Iranian", or "no language is favoured" - it is not obliged
to answer Turkic. That is the whole point.

PRIORS come from ASJP v19 (one dataset, one transcription system for every
family), which keeps prior QUALITY comparable across languages. Using Clauson
for Turkic and a Swadesh list for Yeniseian would bias the comparison toward
whichever language had the better dictionary.

CONTROLS run first, and they are the reason to believe anything downstream:
  - Ming Uyghur transcriptions (182)  should come out TURKIC
  - Buddhist Sanskrit transcriptions  should come out INDIC
  - Sogdian names in Chinese sources  should come out IRANIAN
If the controls fail, the Xiongnu numbers are meaningless and the script says so.

Stdlib only. Needs asjp-v19.1.zip in Downloads and step 4's output.
"""
import csv, io, os, re, sys, math, zipfile, random
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT  = os.path.join(ROOT, "data", "external")
DER  = os.path.join(ROOT, "data", "derived")
DATA = os.path.join(ROOT, "data")
DL   = os.path.join(ROOT, "Downloads")
REP  = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)

log_lines = []
def log(s=""):
    print(s); log_lines.append(s)
CJK = re.compile(r'[一-鿿㐀-䶿]')
def read_csv(p):
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8-sig") as f: return list(csv.DictReader(f))

log("=" * 70)
log(" STEP 5 - which language best explains the transcription?")
log("=" * 70)
log()

# ------------------------------------------------- common phoneme alphabet
# Everything - Sanskrit syllables from the channel, ASJP word forms - is mapped
# into ASJP's coarse alphabet. Coarse is a feature: it removes distinctions
# (vowel length, aspiration) that Chinese transcription could not record anyway.
SKT2ASJP = [
 ('kh','k'),('gh','g'),('ch','C'),('jh','j'),('ṭh','t'),('ḍh','d'),
 ('th','t'),('dh','d'),('ph','p'),('bh','b'),
 ('ai','aj'),('au','aw'),('ā','a'),('ī','i'),('ū','u'),('ṝ','r'),('ṛ','r'),
 ('ḹ','l'),('ḷ','l'),
 ('ṅ','N'),('ñ','5'),('ṭ','t'),('ḍ','d'),('ṇ','n'),('ś','S'),('ṣ','S'),
 ('ṃ','N'),('ḥ','h'),
 ('c','C'),('j','j'),('k','k'),('g','g'),('t','t'),('d','d'),('n','n'),
 ('p','p'),('b','b'),('m','m'),('y','y'),('r','r'),('l','l'),('v','v'),
 ('s','s'),('h','h'),('a','a'),('i','i'),('u','u'),('e','e'),('o','o'),
]
def to_asjp(s):
    s = (s or "").strip().lower(); out=[]; i=0
    while i < len(s):
        for a,b in SKT2ASJP:
            if s.startswith(a,i): out.append(b); i+=len(a); break
        else: i+=1
    return "".join(out)

ASJP_OK = set("pbfvmw84tdsznrlSZCjT5ykgxNqGX7hL" + "ieE3auo")
def clean_asjp(f):
    return "".join(ch for ch in (f or "") if ch in ASJP_OK)

# ------------------------------------------------------------ ASJP priors
ZP = os.path.join(DL, "asjp-v19.1.zip")
if not os.path.exists(ZP):
    log(f"FATAL: {ZP} not found."); sys.exit(1)

with zipfile.ZipFile(ZP) as z:
    base = next(n for n in z.namelist() if n.endswith("cldf/languages.csv")).rsplit("/",1)[0] + "/"
    langs = {}
    with z.open(base+"languages.csv") as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8")): langs[r["ID"]] = r
    byl = defaultdict(list)
    with z.open(base+"forms.csv") as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8")):
            fm = clean_asjp(r["Form"])
            if fm: byl[r["Language_ID"]].append(fm)

def cls(k): return langs[k].get("classification_glottolog","") or ""
def fam(k): return langs[k].get("Family","") or ""
GROUPS = {
 "Turkic":    [k for k in langs if fam(k)=="Turkic"],
 "Yeniseian": [k for k in langs if fam(k)=="Yeniseian"],
 "Mongolic":  [k for k in langs if fam(k)=="Mongolic-Khitan"],
 "Iranian":   [k for k in langs if "Iranian" in cls(k) and "Indo-Aryan" not in cls(k)],
 "Indic":     [k for k in langs if "Indo-Aryan" in cls(k) or k in ("SANSKRIT","PALI")],
 "Tungusic":  [k for k in langs if fam(k)=="Tungusic"],
}
log("Phonotactic priors from ASJP v19 (all in one transcription system):")
CORPUS = {}
for g, ids in GROUPS.items():
    forms = [w for i in ids for w in byl.get(i, [])]
    CORPUS[g] = forms
    marker = ""
    if g == "Turkic" and "OLD_TURKIC" in ids: marker = "  (includes OLD_TURKIC, CHAGATAI)"
    if g == "Indic":     marker = "  (includes SANSKRIT, PALI)"
    if g == "Iranian":   marker = "  (includes AVESTAN, OLD_PERSIAN)"
    log(f"  {g:10s} {len(ids):4d} doculects  {len(forms):6d} forms{marker}")
log()

ORD = 3
class NGram:
    """Character n-gram with additive smoothing and backoff to shorter contexts."""
    def __init__(self, forms, order=ORD):
        self.order = order
        self.cnt = [defaultdict(Counter) for _ in range(order)]
        self.voc = set()
        for w in forms:
            s = "^"*(order-1) + w + "$"
            self.voc.update(w)
            for i in range(order-1, len(s)):
                for k in range(order):
                    ctx = s[i-k:i]
                    self.cnt[k][ctx][s[i]] += 1
        self.V = max(len(self.voc), 1) + 1
    def logp(self, w):
        s = "^"*(self.order-1) + w + "$"
        tot = 0.0
        for i in range(self.order-1, len(s)):
            ch = s[i]; p = None
            for k in range(self.order-1, -1, -1):
                c = self.cnt[k][s[i-k:i]]
                n = sum(c.values())
                if n >= 3:
                    p = (c[ch] + 0.25) / (n + 0.25*self.V); break
            if p is None:
                c = self.cnt[0][""]; n = sum(c.values()) or 1
                p = (c[ch] + 0.25) / (n + 0.25*self.V)
            tot += math.log(p)
        return tot

# A model fitted on 7,323 Indic forms is SHARP; one fitted on 469 Yeniseian
# forms backs off constantly and is FLAT. A flat model assigns higher
# probability to unusual strings, so it wins by being vague - the comparison
# would measure corpus size, not linguistic fit. So: subsample every family to
# the same number of forms, and average the score over several draws.
usable = {g: f for g, f in CORPUS.items() if len(f) >= 200}
N_EQ = min(len(f) for f in usable.values())
N_DRAWS = 5
log(f"Equalising priors: every family subsampled to {N_EQ} forms "
    f"(the smallest, {min(usable, key=lambda g: len(usable[g]))}),")
log(f"averaged over {N_DRAWS} independent draws. This removes corpus size as a")
log("confound - otherwise the comparison rewards whichever language has the")
log("thinnest data, because its model is flatter.")
log()
random.seed(23)
MODELS = {}
for g, f in usable.items():
    draws = []
    for d in range(N_DRAWS):
        sub = f if len(f) == N_EQ else random.sample(f, N_EQ)
        draws.append(NGram(sub))
    MODELS[g] = draws
LANGS = list(MODELS)
log(f"  fitted: {', '.join(f'{g} ({len(CORPUS[g])} avail)' for g in LANGS)}")
log()

class Ensemble:
    """Average log-probability across the equal-size draws."""
    def __init__(self, models): self.models = models
    def logp(self, w): return sum(m.logp(w) for m in self.models) / len(self.models)
MODELS = {g: Ensemble(d) for g, d in MODELS.items()}

# ------------------------------------------------------- channel emissions
em = read_csv(os.path.join(DER, "channel_emissions.csv"))
if not em:
    log("FATAL: data/derived/channel_emissions.csv missing. Run step 4 first.")
    sys.exit(1)
CAND = defaultdict(list)
for r in em:
    try: CAND[r["chinese_char"]].append((r["source_syllable"], float(r["p_syllable_given_char"])))
    except Exception: pass
for c in CAND: CAND[c].sort(key=lambda x: -x[1])
log(f"Channel table: {len(CAND)} characters with candidate syllables")
log()

# --------------------------------------------------- beam decode + marginal
BEAM, TOPN = 160, 4
def marginal(chars, model):
    """log P(chars | L) via beam search over candidate syllable sequences.
       Returns (logsumexp over the beam, best candidate as an ASJP string)."""
    beams = [("", 0.0)]                      # (asjp string so far, channel logp)
    for c in chars:
        cands = CAND.get(c, [])[:TOPN]
        if not cands: return None, None
        nxt = []
        for pre, lp in beams:
            for syl, p in cands:
                if p <= 0: continue
                nxt.append((pre + to_asjp(syl), lp + math.log(p)))
        nxt.sort(key=lambda t: -(t[1] + model.logp(t[0])))
        beams = nxt[:BEAM]
    if not beams: return None, None
    scored = [(lp + model.logp(w), w) for w, lp in beams]
    m = max(s for s, _ in scored)
    tot = m + math.log(sum(math.exp(s - m) for s, _ in scored))
    best = max(scored, key=lambda t: t[0])[1]
    return tot, best

def compare(chars):
    """-> dict language -> (log marginal, best form), normalised by length."""
    out = {}
    for L, mdl in MODELS.items():
        lm, best = marginal(chars, mdl)
        if lm is not None: out[L] = (lm, best)
    return out

def winner(res):
    if not res: return None, None, 0.0
    order = sorted(res.items(), key=lambda kv: -kv[1][0])
    top, second = order[0], (order[1] if len(order) > 1 else None)
    margin = (top[1][0] - second[1][0]) if second else float("inf")
    return top[0], (second[0] if second else None), margin

# ------------------------------------------------ PRIOR CEILING DIAGNOSTIC
# Before blaming the channel for any failure, establish what the priors alone
# can do. Hand them the TRUE source form - no Chinese, no channel, no
# uncertainty - and ask which language they pick. Whatever this scores is a hard
# CEILING on the full pipeline: the channel can only lose information from here.
log("=" * 70)
log(" PRIOR CEILING - what can the phonotactic priors do on their own?")
log("=" * 70)
log()
log("Given the TRUE source word (bypassing Chinese and the channel entirely),")
log("which language do the priors choose? This bounds everything downstream.")
log()
UY_MAP = {"č":"C","š":"S","ž":"Z","ǰ":"j","ŋ":"N","ɣ":"G","ä":"E","ö":"o","ü":"u",
          "ï":"3","ı":"3","ə":"3","c":"C"}
def uy_to_asjp(w):
    w = "".join(c for c in (w or "").lower() if c.isalpha() or c in "ɣŋčšžǰ")
    return clean_asjp("".join(UY_MAP.get(c, c) for c in w))

def ceiling(strings, label, expect):
    v = Counter(); n = 0
    for a in strings:
        if not a or len(a) < 2: continue
        sc = {L: MODELS[L].logp(a)/len(a) for L in MODELS}
        v[max(sc, key=sc.get)] += 1; n += 1
    if not n:
        log(f"  {label}: nothing scoreable"); return None
    ch = 100.0/len(MODELS)
    log(f"  {label}  (n={n}, expect {expect}, chance {ch:.1f}%)")
    for L, c in v.most_common():
        log(f"      {L:10s} {c:4d}  {100*c/n:5.1f}%" + ("  <-- expected" if L==expect else ""))
    log()
    return v[expect]/n

ceil_tur = ceiling([uy_to_asjp((r["uyghur_variants"] or "").split("|")[-1])
                    for r in read_csv(os.path.join(DER, "uyghur_chinese_pairs.csv"))],
                   "true Uyghur word forms", "Turkic")
random.seed(1)
_sa = read_csv(os.path.join(DER, "nti_transcription_pairs.csv"))
ceil_ind = ceiling([clean_asjp(to_asjp(r["skt"]))
                    for r in random.sample(_sa, min(250, len(_sa)))],
                   "true Sanskrit word forms", "Indic")
log("-" * 70)
if ceil_tur is not None and ceil_ind is not None and max(ceil_tur, ceil_ind) < 0.55:
    log(" CEILING IS LOW. The priors cannot reliably identify a language even when")
    log(" handed the actual word. The bottleneck is the PRIOR, not the channel.")
    log(" Root causes:")
    log("   - ASJP is a deliberately coarse 41-symbol alphabet; it discards exactly")
    log("     the detail that separates neighbouring families.")
    log(f"   - equalising to {N_EQ} forms per family (the Yeniseian floor) leaves very")
    log("     little data to fit a 3-gram on.")
    log("   - Swadesh entries are SHORT; a 5-segment word carries little phonotactic")
    log("     signal either way.")
    log("   - Turkic, Mongolic and Tungusic are phonotactically near-identical")
    log("     (vowel harmony, agglutinating, similar inventories and syllable shape).")
    log("     Generic n-grams cannot separate them from one short word, and no amount")
    log("     of channel improvement will fix that.")
    log()
    log(" WHAT WOULD FIX IT - targeted linguistic constraints instead of n-grams:")
    log("   * vowel harmony consistency  - strong in Turkic, absent in Yeniseian")
    log("   * initial-segment constraints - Old Turkic bans initial l-, r-, n-,")
    log("     and bans initial clusters; Yeniseian permits both")
    log("   * permitted codas and syllable shapes")
    log("   These are few-parameter features that work on short words, which is")
    log("   exactly the regime here. Generic n-grams are the wrong tool.")
    log()
    log(" Also consider narrowing the question to the live debate - Turkic vs")
    log(" Yeniseian - rather than six families at once. Yeniseian is the most")
    log(" phonotactically distinct of the set, and binary chance is 50%.")
log("-" * 70)
log()

# ------------------------------------------------------------- CONTROLS
log("=" * 70)
log(" CONTROLS - full pipeline, from Chinese characters")
log("=" * 70)
log()

def run_set(items, label, expect, cap=140):
    random.seed(5)
    if len(items) > cap: items = random.sample(items, cap)
    votes = Counter(); margins = []
    for chars in items:
        res = compare(chars)
        w, s, m = winner(res)
        if w is None: continue
        votes[w] += 1
        if m != float("inf"): margins.append(m)
    n = sum(votes.values())
    if not n:
        log(f"  {label}: nothing scoreable"); return None
    log(f"  {label}  (n={n}, expected: {expect})")
    for L, v in votes.most_common():
        mark = "  <-- expected" if L == expect else ""
        log(f"      {L:10s} {v:4d}  {100*v/n:5.1f}%{mark}")
    acc = votes[expect]/n
    chance = 1.0/max(1, len(LANGS))
    log(f"      accuracy on the expected language: {100*acc:.1f}%   "
        f"(chance = {100*chance:.1f}%)")
    log()
    return acc

# Turkic control: the Ming Uyghur transcriptions
uy = [CJK.findall(r["chinese"] or "") for r in read_csv(os.path.join(DER, "uyghur_chinese_pairs.csv"))]
uy = [c for c in uy if c]
acc_tur = run_set(uy, "Ming Uyghur transcriptions", "Turkic")

# Indic control: verified Buddhist Sanskrit transcriptions
sa = [CJK.findall(r["trad"] or "") for r in read_csv(os.path.join(DER, "nti_transcription_pairs.csv"))]
sa = [c for c in sa if c]
acc_ind = run_set(sa, "Buddhist Sanskrit transcriptions", "Indic")

# Iranian control: Sogdian names (tiny - reported for completeness)
sog = [CJK.findall(r["chinese"] or "") for r in read_csv(os.path.join(DATA, "control_sets.csv"))
       if (r.get("language") or "") == "Sogdian"]
sog = [c for c in sog if c]
acc_ira = run_set(sog, "Sogdian names in Chinese sources", "Iranian") if sog else None

chance = 1.0/max(1, len(LANGS))
def beats(a): return a is not None and a >= max(2.0*chance, chance + 0.15)
controls_ok = beats(acc_tur) and beats(acc_ind)
log("-" * 70)
if controls_ok:
    log(" CONTROLS PASS. The method recovers the language of transcriptions whose")
    log(" source language is not in dispute. Proceeding to the Xiongnu material.")
else:
    log(" CONTROLS FAIL. The method cannot reliably recover languages it should")
    log(" already know, so any verdict it gives on the Xiongnu is worthless.")
    log(" Do not report the numbers below as evidence of anything.")
log("-" * 70)
log()

# ------------------------------------------------------------- XIONGNU
log("=" * 70)
log(" XIONGNU MATERIAL")
log("=" * 70)
log()
rows = (read_csv(os.path.join(DER, "xiongnu_rulers_reconstructed.csv")) +
        read_csv(os.path.join(DER, "xiongnu_titles_lexicon_reconstructed.csv")))
results, votes = [], Counter()
for r in rows:
    chars = CJK.findall(r.get("chinese") or "")
    if not chars: continue
    res = compare(chars)
    w, s, m = winner(res)
    if w is None: continue
    votes[w] += 1
    row = {"chinese": r.get("chinese",""), "pinyin": r.get("pinyin_modern",""),
           "entry_type": r.get("entry_type",""), "best_language": w,
           "runner_up": s or "", "log_bayes_factor": round(m,2) if m != float("inf") else "",
           "best_form": res[w][1], "proposed_reading": r.get("proposed_reading","")}
    for L in LANGS:
        row[f"logP_{L}"] = round(res[L][0],2) if L in res else ""
    results.append(row)

log(f"{'name':8s} {'best':10s} {'2nd':10s} {'logBF':>7s}  {'form':12s} literature")
log("-" * 70)
for r in results:
    lit = f"{r['proposed_reading']}" if r["proposed_reading"] else ""
    log(f"{r['chinese']:8s} {r['best_language']:10s} {r['runner_up']:10s} "
        f"{str(r['log_bayes_factor']):>7s}  {r['best_form']:12s} {lit}")
log()
n = sum(votes.values())
log(f"Distribution over {n} items:")
for L, v in votes.most_common():
    log(f"  {L:10s} {v:3d}  {100*v/n:5.1f}%")
log()

# how decisive is any of this?
strong = [r for r in results if isinstance(r["log_bayes_factor"], float) and r["log_bayes_factor"] >= 2.3]
log(f"Items with a decisive margin (log BF >= 2.3, i.e. 10:1): "
    f"{len(strong)}/{len(results)}")
log()
if not controls_ok:
    log("READ NOTHING INTO THE ABOVE - the controls failed.")
elif len(strong) < 0.3*len(results):
    log("INTERPRETATION: mostly INCONCLUSIVE. Few items reach a 10:1 margin, so the")
    log("evidence does not separate the hypotheses for most names. With ~39 items and")
    log("Swadesh-list priors that is the expected and honest outcome - and it is a")
    log("publishable finding in a debate this contested.")
else:
    top = votes.most_common(1)[0]
    log(f"INTERPRETATION: {top[0]} leads on {top[1]}/{n} items, and {len(strong)} items")
    log("reach a 10:1 margin. Treat as provisional, not settled - see the caveats.")
log()
log("CAVEATS that limit every number above:")
log("  1. Priors are ASJP Swadesh-list BASIC VOCABULARY. Personal names and titles")
log("     have different phonotactics from everyday words. This is the single")
log("     biggest weakness.")
log("  2. Priors come from modern or medieval attestations, not Xiongnu-era forms.")
log("     OLD_TURKIC and CHAGATAI help on the Turkic side; Yeniseian has no old")
log("     attestation at all, which disadvantages it unfairly.")
log("  3. The channel was trained on Sanskrit. It transfers (step 4), but it has")
log("     seen no Turkic or Yeniseian transcription conventions.")
log("  4. Names travel across languages. A Turkic-looking royal name is compatible")
log("     with a non-Turkic-speaking population.")
log("  5. n is tiny.")

with open(os.path.join(DER, "language_comparison.csv"), "w", newline="", encoding="utf-8-sig") as f:
    if results:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader(); w.writerows(results)
log()
log("Written to data/derived/language_comparison.csv")
with open(os.path.join(REP, "step5_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")
print("\nSummary written to reports/step5_summary.txt")
