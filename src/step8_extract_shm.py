#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 8 - extract the Secret History of the Mongols transcription corpus.

WHY THIS MATTERS. Every negative result so far (steps 5-7) is compatible with two
different explanations: the method is wrong, or 1,017 Sanskrit pairs is not enough
data. Those are confounded, and until they are separated there is no way to know
whether the segmental redesign is worth attempting.

The Secret History breaks the confound. It is a full Mongolian text written in
Chinese characters with a romanised reading beside it - a genuine running
transcription, not a dictionary, so no calque contamination. Order of ~29,000
pairs against the current 1,017.

FORMAT. The epub stores each item as a TRIPLE, fields delimited by U+200B:

    <Chinese gloss>  <Chinese transcription>  <romanised Mongolian>
    百姓 行           亦 舌᠋ 兒堅-突︀ 舌᠋ 兒        irgen-dur

The transcription carries traditional reading annotations: a Chinese character
followed by MONGOLIAN FREE VARIATION SELECTOR ONE (U+180B) is an ANNOTATION on
the character after it (舌 = liquid/retroflex reading, 中 = medial, 灰), not part
of the transcription, and must be dropped. Characters carrying U+180C or U+FE00
ARE transcription characters (marking a final consonant, or a variant graph) and
must be kept with the selector stripped.

Verified on the probe sample: 92% of pairs agree within +/-1 between character
count and romanised syllable count, which is the expected signature of a genuine
per-syllable transcription.

Writes the corpus locally and a SMALL report. Stdlib only.
"""
import csv, html, os, re, sys, zipfile
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL   = os.path.join(ROOT, "Downloads")
DER  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
for d in (DER, REP): os.makedirs(d, exist_ok=True)

CJK   = re.compile(r'[㐀-䶿一-鿿]')
LAT   = re.compile(r'[a-zA-Z]')
SEL   = re.compile(r'[᠋-᠏︀-️]')
ANNOT = re.compile(r'[㐀-䶿一-鿿]᠋')          # annotation char + FVS1
PAREN = re.compile(r'[（(][^）)]*[）)]')
TAG   = re.compile(r'<[^>]+>')
ZWSP  = "​"

out = []
def log(s=""):
    print(s); out.append(s)

def clean_tr(s):
    s = ANNOT.sub('', s)
    s = SEL.sub('', s)
    s = PAREN.sub('', s)
    return ''.join(CJK.findall(s))

def clean_ro(s):
    s = PAREN.sub('', s)
    return s.strip().strip('".,;:!?“”’‘ ')

def kind(t):
    c, l = bool(CJK.search(t)), bool(LAT.search(t))
    return "C" if c and not l else ("L" if l and not c else ("M" if c and l else "-"))

V = set("aeiouäöüïıāēīōūáéíóúəɨ")
def nsyl(w):
    w = w.lower(); n = 0
    for i, c in enumerate(w):
        if c in V and (i == 0 or w[i-1] not in V): n += 1
    return n

log("=" * 68)
log(" STEP 8 - extract the Secret History of the Mongols corpus")
log("=" * 68)
log()
cands = [f for f in os.listdir(DL) if f.lower().endswith(".epub")] if os.path.isdir(DL) else []
if not cands:
    log("FATAL: no .epub in Downloads/."); sys.exit(1)
path = os.path.join(DL, cands[0])
log(f"source: {cands[0]}  ({os.path.getsize(path):,} bytes)")
log()

def lines_of(z, n):
    raw = z.read(n).decode("utf-8", "replace")
    raw = re.sub(r'(?is)<(script|style).*?</\1>', ' ', raw)
    raw = re.sub(r'(?i)</(p|div|tr|td|li|h[1-6])\s*>', '\n', raw)
    raw = re.sub(r'(?i)<br\s*/?>', '\n', raw)
    txt = html.unescape(TAG.sub(' ', raw))
    return [l.strip() for l in txt.split("\n")]

triples, per_doc = [], Counter()
with zipfile.ZipFile(path) as z:
    docs = [n for n in z.namelist()
            if n.lower().endswith((".xhtml", ".html", ".htm"))
            and "nav" not in n.lower() and "toc" not in n.lower()]
    for n in sorted(docs):
        for L in lines_of(z, n):
            if ZWSP not in L: continue
            toks = [t.strip() for t in L.split(ZWSP)]
            toks = [t for t in toks if t]
            ks = [kind(t) for t in toks]
            i = 0
            while i + 2 < len(toks):
                if ks[i] == "C" and ks[i+1] == "C" and ks[i+2] == "L":
                    gl = clean_tr(toks[i]); tr = clean_tr(toks[i+1]); ro = clean_ro(toks[i+2])
                    if tr and ro and LAT.search(ro):
                        triples.append({"source_doc": n.rsplit("/",1)[-1],
                                        "gloss_zh": gl, "chinese": tr, "mongolian": ro,
                                        "n_chars": len(tr), "n_syl": nsyl(ro)})
                        per_doc[n.rsplit("/",1)[-1]] += 1
                    i += 3
                else:
                    i += 1

log(f"triples extracted            : {len(triples):,}")
if not triples:
    log("FATAL: nothing extracted - the epub layout may differ from the probe.")
    with open(os.path.join(REP,"step8_summary.txt"),"w",encoding="utf-8") as f:
        f.write("\n".join(out)+"\n")
    sys.exit(1)

uniq = {}
for t in triples:
    uniq.setdefault((t["chinese"], t["mongolian"]), t)
log(f"unique (chinese, mongolian)  : {len(uniq):,}")
chars = Counter(c for t in triples for c in t["chinese"])
log(f"distinct Chinese characters  : {len(chars):,}")
log(f"distinct Mongolian forms     : {len({t['mongolian'] for t in triples}):,}")
log(f"documents contributing       : {len(per_doc)}")
log()

agree = sum(1 for t in triples if abs(t["n_chars"] - t["n_syl"]) <= 1)
exact = sum(1 for t in triples if t["n_chars"] == t["n_syl"])
log("SANITY - character count vs romanised syllable count:")
log(f"  exact match      : {100*exact/len(triples):5.1f}%")
log(f"  within +/-1      : {100*agree/len(triples):5.1f}%")
log("  (a genuine per-syllable transcription should sit high here; the probe")
log("   sample gave 92% within +/-1)")
log()

log("SAMPLE - 20 extracted pairs:")
log(f"  {'gloss':10s} {'transcription':14s} mongolian")
for t in triples[:20]:
    log(f"  {t['gloss_zh'][:10]:10s} {t['chinese'][:14]:14s} {t['mongolian']}")
log()
log(f"Most frequent transcription characters:")
log("  " + "  ".join(f"{c}({n})" for c, n in chars.most_common(20)))
log()

# scale comparison against what the channel currently trains on
cur = os.path.join(DER, "nti_transcription_pairs.csv")
n_cur = 0
if os.path.exists(cur):
    with open(cur, encoding="utf-8-sig") as f: n_cur = sum(1 for _ in csv.DictReader(f))
log("SCALE:")
log(f"  current channel training set (Sanskrit) : {n_cur:,} pairs")
log(f"  this corpus (Mongolian)                 : {len(uniq):,} unique pairs")
if n_cur: log(f"  factor                                  : {len(uniq)/n_cur:.1f}x")
log()
log("PERIOD NOTE: this is Yuan-era material, so the Chinese side belongs to the")
log("Old Mandarin layer, not the Later Han layer the Xiongnu names need. That is")
log("fine for its purpose here - the question this corpus answers is whether the")
log("METHOD works when data is adequate, which is currently confounded with the")
log("data being thin. Period transfer is a separate question.")

with open(os.path.join(DER, "shm_transcription_pairs.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["source_doc","gloss_zh","chinese","mongolian","n_chars","n_syl"])
    w.writeheader(); w.writerows(uniq.values())
log()
log(f"Written to data/derived/shm_transcription_pairs.csv ({len(uniq):,} rows)")
with open(os.path.join(REP, "step8_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\nSummary written to reports/step8_summary.txt")
