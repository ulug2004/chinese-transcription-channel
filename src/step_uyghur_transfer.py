#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turkic transfer test.

Two jobs:
  A. Extract what the UW thesis (Tan 2019) actually publishes:
       - the appendix tables: Chinese characters with PULLEYBLANK (1991) Early
         Middle Chinese and Níng (1985) Old Mandarin reconstructions
       - the numbered body examples: Chinese gloss + Chinese transcription +
         Uyghur romanisations
  B. Test whether onset-compatibility - the mechanism that separated Sanskrit
     transcriptions from calques in step 1 - also holds for Turkic. If it does
     not, the cross-lingual transfer the project depends on does not work, and
     that needs to be known now.

    !! CORRECTION to an earlier claim in references/corpus_audit.md !!
    The thesis does NOT reproduce 1,040 Uyghur-Chinese term pairs. It ANALYSES
    1,040 terms, but those terms live in Hu & Huang (1984), 高昌館雜字對照分類詞匯,
    a print book. The thesis publishes only ~180 illustrative examples plus
    184 characters in the coda tables. The corpus_audit entry was wrong.

Needs: pdfplumber (pip install pdfplumber). Everything else is stdlib.
"""
import csv, os, re, sys, zipfile, random
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT  = os.path.join(ROOT, "data", "external")
DL   = os.path.join(ROOT, "Downloads")
OUT  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
for d in (OUT, REP): os.makedirs(d, exist_ok=True)

PDF = os.path.join(DL, "UW_thesis_Ming_Uyghur_transcriptions.pdf")
CJK = re.compile(r'[一-鿿㐀-䶿]')
CJKRUN = re.compile(r'[一-鿿㐀-䶿]+')

log_lines = []
def log(s=""):
    print(s); log_lines.append(s)

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber is not installed.\n"
          "  Install it with:   pip install pdfplumber\n"
          "  (RUN-uyghur.bat offers to do this for you.)")
    sys.exit(1)

if not os.path.exists(PDF):
    print(f"ERROR: {PDF} not found."); sys.exit(1)

# ------------------------------------------------------- PDF row extraction
def rows_of(page, ytol=7.0, xgap=12.0):
    """Group words into table rows by vertical midpoint, then into cells by x-gaps.
       pdfplumber's layout=True mode mangles these tables; coordinates do not."""
    ws = [w for w in page.extract_words(use_text_flow=False) if w["text"].strip()]
    for w in ws: w["mid"] = (w["top"] + w["bottom"]) / 2.0
    ws.sort(key=lambda w: (w["mid"], w["x0"]))
    rows = []
    for w in ws:
        if rows and abs(w["mid"] - rows[-1][0]) <= ytol:
            rows[-1][1].append(w)
            n = len(rows[-1][1])
            rows[-1][0] = (rows[-1][0] * (n - 1) + w["mid"]) / n
        else:
            rows.append([w["mid"], [w]])
    out = []
    for _, r in rows:
        r.sort(key=lambda w: w["x0"])
        cols, cell = [], [r[0]]
        for prev, w in zip(r, r[1:]):
            if w["x0"] - prev["x1"] > xgap: cols.append(cell); cell = [w]
            else: cell.append(w)
        cols.append(cell)
        out.append([" ".join(x["text"] for x in c) for c in cols])
    return out

log("=" * 66)
log(" TURKIC TRANSFER TEST")
log("=" * 66)
log()
log("Extracting from the UW thesis (166 pages)...")

appendix, examples = [], []
CODA_BY_TABLE = {"I": "-m", "II": "-n", "III": "-ng", "IV": "-p", "V": "-t", "VI": "-k"}
cur_coda = ""
with pdfplumber.open(PDF) as pdf:
    for pg in pdf.pages:
        rs = rows_of(pg)
        flat = " ".join(" ".join(r) for r in rs)
        m = re.search(r'Table (I|II|III|IV|V|VI)\.\s*G', flat)
        if m: cur_coda = CODA_BY_TABLE.get(m.group(1), "")
        for r in rs:
            # --- appendix table row: idx | pinyin+char | she | MC | ZYYY | OM
            if (len(r) >= 5 and re.fullmatch(r'\d{1,3}', r[0]) and CJK.search(r[1] or "")
                    and CJK.search(r[2] or "")):
                chars = CJKRUN.findall(r[1])
                appendix.append({
                    "coda": cur_coda,
                    "idx": r[0],
                    "pinyin": re.sub(r'[^A-Za-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüĕŭ]', '', r[1].split()[0]),
                    "char": chars[0][0] if chars else "",
                    "char_variants": "/".join(chars[0]) if chars and len(chars[0]) > 1 else "",
                    "she": re.sub(r'\d+$', '', r[2]),
                    "mc_pulleyblank": re.sub(r'\d+$', '', r[3]).strip(),
                    "zyyy": re.sub(r'\d+$', '', r[4]).strip() if len(r) > 4 else "",
                    "om_ning": re.sub(r'\d+$', '', r[5]).strip() if len(r) > 5 else "",
                })
                continue
            # --- body example: "N. gloss | transcription | rom1 | rom2 | ..."
            if not r or not re.match(r'^\d{1,3}\.', r[0]): continue
            first = re.sub(r'^\d{1,3}\.\s*', '', r[0])
            gl = CJKRUN.findall(first)
            if not gl or len(r) < 3: continue
            tr = CJKRUN.findall(r[1] or "")
            if not tr: continue
            # strip trailing footnote markers (e.g. "nuta32" -> "nuta")
            roms = [re.sub(r'\d+$', '', c.strip()) for c in r[2:] if c.strip()]
            if not roms or not re.search(r'[a-zäöüïğčšñŋəḳɣžǰ]', " ".join(roms), re.I): continue
            examples.append({"idx": r[0].split(".")[0], "gloss": gl[0],
                             "chinese": tr[0], "uyghur_variants": " | ".join(roms)})

# The table headers are not reliably detected on every page, which mislabels
# rows. The coda is recoverable from the reconstruction itself - far safer.
CODA_OF = {"m":"-m","n":"-n","ŋ":"-ng","p":"-p","t":"-t","k":"-k"}
for a in appendix:
    mc = (a["mc_pulleyblank"] or "").strip()
    a["coda"] = CODA_OF.get(mc[-1], a["coda"]) if mc else a["coda"]

log(f"  appendix character rows : {len(appendix)}")
log(f"  body example word pairs : {len(examples)}")
log()
log("!! Correction: the thesis does NOT publish 1,040 Uyghur-Chinese pairs.")
log("   It analyses 1,040 terms from Hu & Huang (1984), a PRINT book. What is")
log("   actually here is the two counts above. corpus_audit.md was wrong.")
log()

by_coda = Counter(a["coda"] for a in appendix)
log(f"Appendix by coda: {dict(by_coda)}")
log(f"Characters carrying a Pulleyblank (1991) EMC reconstruction: "
    f"{sum(1 for a in appendix if a['mc_pulleyblank'])}")
log("  ^ worth noting: Pulleyblank is otherwise print-only and undigitised.")
log()

# ------------------------------------------------------------ write extracts
with open(os.path.join(OUT, "uyghur_coda_characters.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["coda","idx","pinyin","char","char_variants",
                                      "she","mc_pulleyblank","zyyy","om_ning"])
    w.writeheader(); w.writerows(appendix)
with open(os.path.join(OUT, "uyghur_chinese_pairs.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["idx","gloss","chinese","uyghur_variants"])
    w.writeheader(); w.writerows(examples)

# ------------------------------------------------------- the transfer test
# Onsets are the stable part of a Chinese syllable across history: initials
# devoiced and palatalised, but PLACE of articulation largely persisted. So Old
# Mandarin (Ning 1985) is used where the appendix supplies it, and Later Han is
# a flagged proxy elsewhere.
OM = {a["char"]: a["om_ning"] for a in appendix if a["om_ning"]}
MC = {a["char"]: a["mc_pulleyblank"] for a in appendix if a["mc_pulleyblank"]}

def load_lhan():
    p = os.path.join(EXT, "LHantab.tsv")
    if not os.path.exists(p): return {}
    rows = list(csv.reader(open(p, encoding="utf-8"), delimiter="\t"))
    h = rows[0]; zi = h.index("zi") if "zi" in h else 1
    sy = h.index("syl_bok") if "syl_bok" in h else len(h)-2
    d = defaultdict(list)
    for r in rows[1:]:
        if len(r) > max(zi, sy) and len(r[zi]) == 1 and r[sy]: d[r[zi]].append(r[sy])
    return d
LHAN = load_lhan()

C_SYMS = ['tsʰ','tʂʰ','tɕʰ','tśʰ','dź','tʂ','tɕ','tś','ts','dz','kʰ','pʰ','tʰ','ṭʰ',
          'ḍ','ṭ','ṇ','ʂ','ʐ','ṣ','ś','ź','ŋ','ɦ','ʔ','x','γ','ɣ','k','g','q','p','b','m',
          't','d','n','s','z','h','j','w','l','r','f','v','č','š','ž','ǰ','y']
def initial(s):
    s = (s or "").strip()
    for c in C_SYMS:
        if s.startswith(c): return c
    return ""

TUR_V = set("aeiouäöüïıəɨAEIOU")
def tur_onsets(w):
    """Onsets of each syllable in a Turkic romanisation."""
    w = w.strip().lower(); out=[]; cur=[]
    i = 0
    while i < len(w):
        ch = w[i]
        if ch in TUR_V:
            out.append("".join(cur)); cur=[]
        elif ch.isalpha() or ch in "ɣŋčšžǰḳ":
            cur.append(ch)
        else:
            cur=[]                       # hyphen / space resets
        i += 1
    return out

# Two sets of equivalence classes. LOOSE lumps all sibilants and affricates
# together and merges l/r/n - generous, and generosity inflates match rates.
# TIGHT keeps them apart. Reporting both is the honest way to show the result is
# not an artefact of how broadly the classes were drawn.
GROUPS_LOOSE = [
    ({'p','pʰ','b','m','f','v'},                     {'p','b','m','v','w'}),
    ({'t','tʰ','d','n','ṭ','ṭʰ','ḍ','ṇ'},            {'t','d','n'}),
    ({'k','kʰ','g','ŋ','x','γ','ɣ','q','h','ɦ'},     {'k','g','q','ɣ','x','ŋ','h'}),
    ({'ts','tsʰ','dz','tʂ','tʂʰ','tɕ','tɕʰ','tś','tśʰ','dź','ʂ','ʐ','s','z','ś','ź','ṣ','č','š','ž','ǰ'},
                                                     {'s','š','z','ž','č','ǰ','c','j'}),
    ({'l','r','n'},                                  {'l','r','n'}),
    ({'j','y','ʔ','ɦ','h','w','v',''},               {'y','v','w','h',''}),
]
GROUPS_TIGHT = [
    ({'p','pʰ','b','f'},                             {'p','b'}),
    ({'m'},                                          {'m'}),
    ({'t','tʰ','d','ṭ','ṭʰ','ḍ'},                    {'t','d'}),
    ({'n','ṇ'},                                      {'n'}),
    ({'k','kʰ','g','x','γ','ɣ','q'},                 {'k','g','q','ɣ','x'}),
    ({'ŋ'},                                          {'ŋ'}),
    ({'s','z','ʂ','ʐ','ś','ź','ṣ'},                  {'s','š','z','ž'}),
    ({'ts','tsʰ','dz','tʂ','tʂʰ','tɕ','tɕʰ','tś','tśʰ','dź','č','ǰ'},
                                                     {'č','ǰ','c','j'}),
    ({'l'},                                          {'l','r'}),
    ({'r'},                                          {'r','l'}),
    ({'j','y'},                                      {'y'}),
    ({'w','v'},                                      {'v','w'}),
    ({'ʔ','ɦ','h',''},                               {'h',''}),
]
def compatible(ci, to, groups=GROUPS_LOOSE):
    if ci == to: return True
    for L, T in groups:
        if ci in L and to in T: return True
    if len(to) > 1:
        for part in (to[:1], to[-1:]):
            for L, T in groups:
                if ci in L and part in T: return True
    return False

def reading_of(c):
    if c in OM:   return OM[c], "OM"
    if c in MC:   return MC[c], "MC"
    if c in LHAN: return LHAN[c][0], "LHan(proxy)"
    return None, None

def score_onsets(chars, ons, groups):
    n = min(len(chars), len(ons))
    ok = cov = 0
    for c, o in zip(chars[:n], ons[:n]):
        rd, _ = reading_of(c)
        if rd is None: continue
        cov += 1
        if compatible(initial(rd), o, groups): ok += 1
    if cov == 0: return None
    return ok / cov, cov, n

def score_pair(chinese, uy, shuffle=False, groups=GROUPS_LOOSE):
    chars = list(chinese)
    ons = tur_onsets(uy)
    if not chars or not ons: return None
    if shuffle:
        ons = ons[:]; random.shuffle(ons)
    return score_onsets(chars, ons, groups)

log("-" * 66)
log(" Transfer test: does onset compatibility hold for Turkic?")
log("-" * 66)
random.seed(11)

# Build the scoreable set once.
items = []
for e in examples:
    uy = e["uyghur_variants"].split("|")[-1].strip()
    ons = tur_onsets(uy)
    if not ons or not e["chinese"]: continue
    if score_onsets(list(e["chinese"]), ons, GROUPS_LOOSE) is None: continue
    items.append({**e, "uyghur_used": uy, "onsets": ons})
skipped = len(examples) - len(items)

if not items:
    log("  No pairs could be scored - no reading coverage. Test inconclusive.")
    verdict_ok = False
else:
    # pool of onset sequences by length, for the random-pairing null
    pool = defaultdict(list)
    for it in items: pool[len(it["onsets"])].append(it["onsets"])

    def run(groups):
        real, cov_tot = [], 0
        for it in items:
            r = score_onsets(list(it["chinese"]), it["onsets"], groups)
            if r: real.append(r[0]); cov_tot += r[1]
        # NULL 1 - shuffle onsets within the same word (weak: keeps the inventory)
        shuf = []
        for it in items:
            o = it["onsets"][:]; random.shuffle(o)
            r = score_onsets(list(it["chinese"]), o, groups)
            if r: shuf.append(r[0])
        # NULL 2 - pair with a DIFFERENT Uyghur word of the same syllable count
        perm_means = []
        for _ in range(200):
            vals = []
            for it in items:
                cands = pool[len(it["onsets"])]
                if len(cands) < 2: continue
                o = random.choice(cands)
                if o is it["onsets"]: continue
                r = score_onsets(list(it["chinese"]), o, groups)
                if r: vals.append(r[0])
            if vals: perm_means.append(sum(vals)/len(vals))
        mr = sum(real)/len(real)
        ms = sum(shuf)/len(shuf) if shuf else 0.0
        mp = sum(perm_means)/len(perm_means) if perm_means else 0.0
        beat = sum(1 for x in perm_means if x >= mr)
        pval = (beat + 1) / (len(perm_means) + 1) if perm_means else 1.0
        hi = sum(1 for x in real if x >= 0.75)
        return dict(n=len(real), cov=cov_tot, real=mr, shuf=ms, perm=mp,
                    pval=pval, hi=hi, perms=len(perm_means))

    loose = run(GROUPS_LOOSE)
    tight = run(GROUPS_TIGHT)

    log(f"  pairs scored              : {loose['n']}  (skipped for no coverage: {skipped})")
    log(f"  character positions scored: {loose['cov']}")
    log()
    log("                              LOOSE classes   TIGHT classes")
    log(f"  observed onset match      :     {loose['real']:.3f}           {tight['real']:.3f}")
    log(f"  null 1 - shuffled onsets  :     {loose['shuf']:.3f}           {tight['shuf']:.3f}   (weak null)")
    log(f"  null 2 - random re-pairing:     {loose['perm']:.3f}           {tight['perm']:.3f}   (strong null)")
    log(f"  lift over strong null     :    {loose['real']-loose['perm']:+.3f}          {tight['real']-tight['perm']:+.3f}")
    log(f"  permutation p             :    {loose['pval']:.4f}          {tight['pval']:.4f}   "
        f"({loose['perms']} permutations)")
    log(f"  pairs at >=0.75 match     :  {loose['hi']}/{loose['n']} ({100*loose['hi']/loose['n']:.0f}%)"
        f"        {tight['hi']}/{tight['n']} ({100*tight['hi']/tight['n']:.0f}%)")
    log()
    log("  Null 1 shuffles onsets inside the same word, so it preserves that")
    log("  word's onset inventory - a two-syllable word matches ~50% by accident.")
    log("  Null 2 pairs each Chinese transcription with a DIFFERENT Uyghur word of")
    log("  the same syllable count. That is the null that matters.")
    log()

    strong_lift = tight["real"] - tight["perm"]
    verdict_ok = (strong_lift >= 0.20 and tight["pval"] < 0.01)
    if verdict_ok:
        log("  VERDICT: transfer is REAL and survives the strong null under TIGHT")
        log("  equivalence classes. A mechanism built for Sanskrit predicts Turkic")
        log("  transcriptions well above chance. The cross-lingual design holds -")
        log("  proceed to the channel model.")
    elif strong_lift >= 0.10 and tight["pval"] < 0.05:
        log("  VERDICT: signal present but MODEST once the strong null and tight")
        log("  classes are applied. Real, probably not strong enough to carry an")
        log("  argument on its own. Get more Turkic pairs (Hu & Huang 1984) before")
        log("  drawing conclusions from it.")
    else:
        log("  VERDICT: NO RELIABLE TRANSFER once properly controlled. The earlier")
        log("  loose-class, weak-null result was an artefact. Do not build on this")
        log("  until the reading layer and the sample are addressed.")

detail = []
for it in items:
    r = score_onsets(list(it["chinese"]), it["onsets"], GROUPS_LOOSE)
    t = score_onsets(list(it["chinese"]), it["onsets"], GROUPS_TIGHT)
    detail.append({"idx": it["idx"], "gloss": it["gloss"], "chinese": it["chinese"],
                   "uyghur_variants": it["uyghur_variants"], "uyghur_used": it["uyghur_used"],
                   "match_loose": round(r[0],3) if r else "",
                   "match_tight": round(t[0],3) if t else "",
                   "positions_scored": r[1] if r else 0})
log()
with open(os.path.join(OUT, "uyghur_transfer_detail.csv"), "w", newline="", encoding="utf-8-sig") as f:
    if detail:
        w = csv.DictWriter(f, fieldnames=list(detail[0].keys()))
        w.writeheader(); w.writerows(detail)

log()
log("Written to data/derived/:")
log(f"  uyghur_coda_characters.csv    {len(appendix)} rows (incl. Pulleyblank EMC)")
log(f"  uyghur_chinese_pairs.csv      {len(examples)} rows")
log(f"  uyghur_transfer_detail.csv    {len(detail)} rows")

with open(os.path.join(REP, "step_uyghur_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")
print("\nSummary written to reports/step_uyghur_summary.txt")
