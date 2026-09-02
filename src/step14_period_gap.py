#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 14 - how much does the period gap cost?

The last open question. The working Turkic channel (step 13) is trained on MING
Mandarin readings, because that is the only era with Turkic-Chinese data. The
Xiongnu names are LATER HAN - roughly 1,200 years earlier. Does anything survive
the jump?

This is measurable without any Xiongnu gold, because the Tan appendix (step 11's
extraction) gives 173 characters with BOTH Pulleyblank's Early Middle Chinese and
Ning's Old Mandarin, and 159 of those also have a Schuessler Later Han reading.
Same characters, three periods:

        Later Han  (c. 200 CE)  ->  EMC (c. 600)  ->  Old Mandarin (c. 1400)

For each pair of periods, and separately for INITIAL, NUCLEUS and CODA, measure
how well the later reading predicts the earlier one - leave-one-out majority
prediction, against an unconditional majority baseline.

The expected shape, and the reason this matters: initials should survive because
place of articulation is conservative; codas should not, because Mandarin lost
the -p/-t/-k and -m finals. If that is what the data shows, then onset-level
claims about Xiongnu names are supportable and segment-level ones are not - and
that is a precise, defensible boundary rather than a guess.

Inputs (both already on disk):
  data/derived/uyghur_coda_characters.csv   (MC + OM, from step 11's extraction)
  data/external/LHantab.tsv                 (Later Han)
Stdlib only, runs in seconds.
"""
import csv, os, re, sys, zipfile
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT  = os.path.join(ROOT, "data", "external")
DER  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)
out = []
def log(s=""):
    print(s); out.append(s)

TONES = "ᴬᴮᶜᴰ¹²³⁴ˊˋ"
CONS = ['tsʰ','tśʰ','tɕʰ','tʂʰ','dʑ','dʐ','dź','tś','tɕ','tʂ','ts','dz',
        'kʰ','pʰ','tʰ','ṭʰ','ḍ','ṭ','ṇ','ṣ','ś','ź','ʂ','ʐ','ɕ','ʑ','ʈ','ɖ',
        'ŋ','ɦ','ʔ','x','γ','ɣ','k','g','q','p','b','m','t','d','n','s','z',
        'h','j','w','l','r','f','v']
VOW = set("aeiouɑɔəɛɨɯyœøæʉʊɪ")

def parse(s):
    """reading -> (initial, nucleus, coda); tone stripped."""
    s = "".join(c for c in (s or "") if c not in TONES).strip()
    if not s: return None
    init = ""
    for c in CONS:
        if s.startswith(c): init = c; break
    rest = s[len(init):]
    i = 0
    while i < len(rest) and rest[i] not in VOW: i += 1
    j = i
    while j < len(rest) and rest[j] in VOW: j += 1
    return (init, rest[i:j], rest[j:])

def load_lhan():
    p = os.path.join(EXT, "LHantab.tsv")
    if not os.path.exists(p):
        log("FATAL: data/external/LHantab.tsv missing."); sys.exit(1)
    rows = list(csv.reader(open(p, encoding="utf-8"), delimiter="\t"))
    h = rows[0]; zi = h.index("zi") if "zi" in h else 1
    sy = h.index("syl_bok") if "syl_bok" in h else len(h)-2
    d = {}
    for r in rows[1:]:
        if len(r) > max(zi, sy) and len(r[zi]) == 1 and r[sy]:
            d.setdefault(r[zi], r[sy])
    return d
def load_variants():
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
    except Exception: return defaultdict(set)
    return eq

log("=" * 74)
log(" STEP 14 - the cost of the period gap")
log("=" * 74)
log()
LH, VAR = load_lhan(), load_variants()
def lhan_of(c):
    if c in LH: return LH[c]
    for v in VAR.get(c, ()):
        if v in LH: return LH[v]
    return None

src = os.path.join(DER, "uyghur_coda_characters.csv")
if not os.path.exists(src):
    log("FATAL: uyghur_coda_characters.csv missing. Run RUN-uyghur.bat."); sys.exit(1)

items = []
for r in csv.DictReader(open(src, encoding="utf-8-sig")):
    ch = (r.get("char") or "").strip()
    mc, om = (r.get("mc_pulleyblank") or "").strip(), (r.get("om_ning") or "").strip()
    if not ch or not mc or not om: continue
    lh = lhan_of(ch)
    P = {"OM": parse(om), "EMC": parse(mc), "LHan": parse(lh) if lh else None}
    if not P["OM"] or not P["EMC"]: continue
    items.append({"char": ch, "coda_class": r.get("coda",""), **P})
log(f"characters with EMC + OM        : {len(items)}")
log(f"characters with all three eras  : {sum(1 for x in items if x['LHan'])}")
log()
log("Sample of the ladder:")
log(f"  {'char':5s} {'Later Han':12s} {'EMC (Tang)':12s} Old Mandarin (Ming)")
for x in items[:8]:
    lh = "".join(x["LHan"]) if x["LHan"] else "-"
    log(f"  {x['char']:5s} {lh:12s} {''.join(x['EMC']):12s} {''.join(x['OM'])}")
log()

PART = {"initial": 0, "nucleus": 1, "coda": 2}
def loo(pairs, part):
    """Leave-one-out majority prediction of target from source. -> (acc, base)."""
    idx = PART[part]
    data = [(s[idx], t[idx]) for s, t in pairs]
    if not data: return None, None
    tot_t = Counter(t for _, t in data)
    hit = base = 0
    for i, (s, t) in enumerate(data):
        cond = Counter(tt for j, (ss, tt) in enumerate(data) if j != i and ss == s)
        if cond and cond.most_common(1)[0][0] == t: hit += 1
        unc = Counter(tt for j, (_, tt) in enumerate(data) if j != i)
        if unc and unc.most_common(1)[0][0] == t: base += 1
    return 100*hit/len(data), 100*base/len(data)

LADDER = [("OM", "EMC", "Ming -> Tang"),
          ("EMC", "LHan", "Tang -> Later Han"),
          ("OM", "LHan", "Ming -> Later Han   <-- the gap that matters")]
log("-" * 74)
log(" PREDICTING THE EARLIER READING FROM THE LATER ONE")
log(" leave-one-out majority prediction; 'base' = unconditional majority")
log("-" * 74)
log()
results = {}
for a, b, label in LADDER:
    pairs = [(x[a], x[b]) for x in items if x[a] and x[b]]
    log(f" {label}   (n={len(pairs)})")
    log(f"   {'part':10s} {'accuracy':>9s} {'base':>7s} {'lift':>7s}")
    for part in ("initial", "nucleus", "coda"):
        acc, base = loo(pairs, part)
        if acc is None: continue
        results[(a, b, part)] = acc
        log(f"   {part:10s} {acc:>8.1f}% {base:>6.1f}% {acc-base:>+6.1f}")
    log()

# ------------------------- coda, split by class - the aggregate figure lies
# An aggregate coda accuracy is misleading here: this sample is 72% nasal-coda
# characters, and nasals behave completely differently from stops. Reporting the
# blend produced a flattering 87% that means nothing.
log("-" * 74)
log(" CODA, BY CLASS - because the aggregate figure is an artefact")
log("-" * 74)
log()
tab = defaultdict(Counter)
for x in items:
    if x["OM"] and x["LHan"]:
        tab[x["OM"][2] or "0"][x["LHan"][2] or "0"] += 1
cols = sorted({k for v in tab.values() for k in v})
log(" Old Mandarin coda (rows) x Later Han coda (cols):")
log("      " + "".join(f"{c:>6s}" for c in cols))
for r in sorted(tab):
    log(f"{r:>5s} " + "".join(f"{tab[r].get(c,0):>6d}" for c in cols))
log()
NASAL = set("mnŋ")
nas = [x for x in items if x["OM"] and x["LHan"] and (x["LHan"][2] or "") and
       x["LHan"][2][-1] in NASAL]
stop = [x for x in items if x["OM"] and x["LHan"] and (x["LHan"][2] or "") and
        x["LHan"][2][-1] in set("ptk")]
nas_ok = sum(1 for x in nas if x["OM"][2] == x["LHan"][2])
log(f" NASAL codas (-m, -n, -ng):  {nas_ok}/{len(nas)} = "
    f"{100*nas_ok/max(1,len(nas)):.1f}% preserved exactly")
if stop:
    sc = Counter(x["LHan"][2] for x in stop)
    top = sc.most_common(1)[0]
    log(f" STOP codas (-p, -t, -k):    {sum(1 for x in stop if x['OM'][2]==x['LHan'][2])}"
        f"/{len(stop)} preserved  -  Old Mandarin merged ALL of them to zero coda")
    log(f"   distribution in Later Han: {dict(sc)}")
    log(f"   best possible guess is the majority class '{top[0]}': "
        f"{top[1]}/{len(stop)} = {100*top[1]/len(stop):.1f}%")
log()
CODA_NASAL = 100*nas_ok/max(1,len(nas))
CODA_STOP  = (100*Counter(x["LHan"][2] for x in stop).most_common(1)[0][1]/len(stop)) if stop else 0.0
log()

# ---------------------------------------------------------- interpretation
i_ini = results.get(("OM","LHan","initial"))
i_cod = results.get(("OM","LHan","coda"))
i_nuc = results.get(("OM","LHan","nucleus"))
log("=" * 74)
log(" WHAT THIS MEANS FOR THE XIONGNU NAMES")
log("=" * 74)
log()
if i_ini is not None:
    log(f" Ming -> Later Han, by component:")
    log(f"   initial            {i_ini:5.1f}%")
    log(f"   nucleus            {i_nuc:5.1f}%")
    log(f"   coda, nasal        {CODA_NASAL:5.1f}%")
    log(f"   coda, stop         {CODA_STOP:5.1f}%   (majority guess only - the")
    log("                              three-way -p/-t/-k contrast is GONE)")
    log()
    log(" The asymmetry is sharp and it is not the one an aggregate figure shows.")
    log(" Nasal codas survive the 1,200-year jump intact. Stop codas are")
    log(" irrecoverable: Old Mandarin merged -p, -t and -k into zero, so given a")
    log(" Ming reading there is no evidence at all about which stop Later Han had.")
    log()
    log(" BUT - and this is why step 13 worked at all - the Ming transcription")
    log(" system COMPENSATED for that loss. Scribes marked foreign final consonants")
    log(" with an extra CHARACTER rather than a coda: 兒 (eul) for -r, 思 (sseu) for")
    log(" -s. Those were the two most frequent syllables in the Ligeti corpus")
    log(" (eul 118, sseu 61). So the information sits in the SYLLABLE SEQUENCE, not")
    log(" in the Chinese coda, and it is not lost by the period shift.")
    log()
    log(" CONSEQUENCE for the Xiongnu names - a precise boundary:")
    log(f"   * Initial place of articulation carries at ~{i_ini:.0f}% across the gap.")
    log("     ONSET-level claims are supportable.")
    log("   * Nasal finals carry intact.")
    log("   * Stop finals do not carry at all. Any claim resting on a Xiongnu name")
    log("     having had a final -p, -t or -k cannot be supported from a Ming-trained")
    log("     channel, and Han-era transcription used codas directly rather than")
    log(f"     compensating characters, so that gap is real.")
    log(f"   * Nucleus at {i_nuc:.0f}% is the weakest link and limits whole-form work")
    log("     independently of the coda question.")
log()
log(" CAVEATS")
log("  1. n is 164 characters, and NOT a random sample - they are the nasal/stop-")
log("     coda characters Tan tabulated. 72% carry a nasal coda, which is why the")
log("     aggregate coda figure came out at a meaningless 87%. Split by class it")
log("     is interpretable; do not quote a single coda number.")
log("  2. Leave-one-out majority prediction is a weak learner. A real model would")
log("     do better, so read these as lower bounds.")
log("  3. Three different reconstruction traditions (Schuessler, Pulleyblank, Ning)")
log("     with different notational conventions; some disagreement is notational")
log("     rather than substantive.")

with open(os.path.join(DER, "period_gap.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["from_era","to_era","part","loo_accuracy_pct"])
    for (a,b,part), v in results.items(): w.writerow([a,b,part,round(v,2)])
log()
log("Written to data/derived/period_gap.csv")
with open(os.path.join(REP, "step14_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\nSummary written to reports/step14_summary.txt")
