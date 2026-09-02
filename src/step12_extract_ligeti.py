#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 12 - extract the Turkic-Chinese corpus from Ligeti (1966, 1969).

This is the in-domain Turkic training data the project has been blocked on since
step 11, where a Sanskrit-trained channel collapsed out-of-domain (position
accuracy 46% -> 10% on Turkic).

FORMAT. Ligeti prints no Chinese characters. He gives the transcription in EFEO
romanisation, parenthesised, after the Turkic form:

    qatïr (ha-ti-eul) «mulet» I 16b (29a)
    qupïng (hou-p'ing) «cruche, pot» II 4b (59b)
    qurudï (k'ou-lou-ti) «il fait sec» I 8a (14b)

That is a READING, not a character - which suits the reading-anchored channel of
step 11 exactly, since that keys on readings anyway. Mandarin has a closed
syllable inventory, so observations per unit climb faster than they would per
character.

FOUR PARSING TRAPS, all of which cost real yield:
  1. EFEO aspiration uses a TYPOGRAPHIC apostrophe (U+2019), not ASCII '.
  2. Some EFEO forms contain a space: (k'ou-eul-ha pan-ti).
  3. Footnote digits sit between the closing paren and the gloss: (k'ou-che)17 «.
  4. The Turkic form is often NOT at line start - "quru- «devenir sec»: qurudï
     (k'ou-lou-ti)" - so anchoring to the start of a line loses the entry.
  Anchoring at line start with an ASCII-only apostrophe class yields 297 pairs.
  Fixing all four yields 595.

Also note the running-head trap that cost half the pages upstream: journals put
the article title on recto and the AUTHOR NAME on verso, so a head filter must
include "ligeti" (see dump_ligeti_text.py).

Input:  reports/ligeti_glossary_raw.txt  (from RUN-dump-ligeti.bat)
Output: data/derived/ligeti_turkic_chinese_pairs.csv
Stdlib only.
"""
import csv, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DER  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
for d in (DER, REP): os.makedirs(d, exist_ok=True)
out = []
def log(s=""):
    print(s); out.append(s)

SRC = os.path.join(REP, "ligeti_glossary_raw.txt")
if not os.path.exists(SRC):
    print("FATAL: reports/ligeti_glossary_raw.txt missing. Run RUN-dump-ligeti.bat.")
    sys.exit(1)

TURK = r"A-Za-zÀ-ɏḀ-ỿ̀-ͯ\-"
EFEO = r"[a-z][a-z\-’' ]{1,34}"
ENTRY = re.compile(
    r'([' + TURK + r']{2,}(?:\s+[' + TURK + r']{2,}){0,2})'
    r'\s*\((' + EFEO + r')\)'
    r'[\d\s,.°⁰-₟]{0,8}'
    r'\s*[«"]')
BAD = {"sic","water","mathews","cit","op","id","ibid","recte","lire","etc",
       "op cit","ach","am","chin","cf","voir","supra","infra","pl","sing"}
# an EFEO syllable is short lowercase latin, optionally aspirated
SYL_OK = re.compile(r"^[a-z]{1,6}'?[a-z]{0,5}$")

txt = open(SRC, encoding="utf-8").read()
parts = re.split(r'===PAGE (\S+) (\d+)===', txt)
recs = [(parts[i], int(parts[i+1]), parts[i+2]) for i in range(1, len(parts), 3)]

log("=" * 72)
log(" STEP 12 - Turkic-Chinese corpus from Ligeti (1966, 1969)")
log("=" * 72)
log()
log(f"source pages: {len(recs)}  "
    f"(1966: {sum(1 for r in recs if r[0]=='L1966')}, "
    f"1969: {sum(1 for r in recs if r[0]=='L1969')})")
log()

rows, flagged = [], 0
for tag, idx, body in recs:
    flat = " ".join(l.strip() for l in body.split("\n") if l.strip())
    for m in ENTRY.finditer(flat):
        turk = m.group(1).strip()
        efeo = re.sub(r'\s+', ' ', m.group(2)).strip().replace("’", "'")
        if efeo.lower() in BAD or turk.lower() in BAD or len(turk) < 2: continue
        # Drop running-head fragments that leak in when an entry starts a page:
        # "LIGETI abiq", "UN VOCABULAIRE SINO-OUIGOUR DES MING qatir".
        wds = [x for x in turk.split()
               if not (len(x) > 1 and x.isupper()) and x.lower() not in
               ("ligeti","un","des","ming","vocabulaire","sino-ouigour",
                "glossaire","supplementaire","supplémentaire")]
        if not wds: continue
        turk = " ".join(wds[-2:]) if len(wds) > 2 else " ".join(wds)
        if len(turk) < 2: continue
        sylls = [s for s in efeo.replace(" ", "-").split("-") if s]
        if not sylls: continue
        ok = all(SYL_OK.match(s) for s in sylls)
        # LENGTH-RATIO FILTER. The regex sometimes pairs a Turkic form with the
        # EFEO reading of a DIFFERENT entry ("mo-tch'e" with gold "it",
        # "toryon" with "mangnuG"). A genuine per-syllable transcription keeps
        # Chinese syllables roughly proportional to Turkic segments; wild
        # mismatches are mis-pairings, and they were being scored as model
        # errors in step 13.
        nseg = len([c for c in turk if c.strip() and c not in " -"])
        if nseg:
            ratio = nseg / len(sylls)
            if ratio < 1.0 or ratio > 3.6: ok = False
        if not ok: flagged += 1
        gl = flat[m.end():]
        gl = gl.split("»")[0][:60] if "»" in gl[:140] else gl[:50]
        rows.append({"turkic": turk, "efeo_chinese": efeo,
                     "n_syllables": len(sylls), "gloss_fr": gl.strip(),
                     "source": tag, "pdf_page": idx,
                     "suspect": "" if ok else "yes"})

uniq = {}
for r in rows: uniq.setdefault((r["turkic"], r["efeo_chinese"]), r)
clean = [r for r in uniq.values() if not r["suspect"]]

log(f"raw matches            : {len(rows):,}")
log(f"unique pairs           : {len(uniq):,}")
log(f"  clean                : {len(clean):,}")
log(f"  flagged as suspect   : {len(uniq)-len(clean):,}  (kept, marked in the CSV)")
log( "    flags = implausible EFEO syllable shape, or a Turkic-segment to")
log( "    Chinese-syllable ratio outside 1.0-3.6, which indicates a mis-pairing")
log(f"  from 1966 / 1969     : {sum(1 for r in uniq.values() if r['source']=='L1966')}"
    f" / {sum(1 for r in uniq.values() if r['source']=='L1969')}")
log()

syl = Counter()
for r in clean:
    for s in r["efeo_chinese"].replace(" ", "-").split("-"):
        if s: syl[s] += 1
tok = sum(syl.values())
log("THE NUMBER THAT MATTERS - observations per unit (see step 10):")
log(f"  distinct EFEO syllables : {len(syl)}")
log(f"  syllable tokens         : {tok:,}")
log(f"  observations / syllable : {tok/max(1,len(syl)):.1f}")
log()
log("  For comparison, from step 10's learning curve:")
log("    Mongolian, full corpus   60.8   -> 36.4% exact, 89.3% within-2")
log("    Mongolian, 2,000 pairs   23.8   -> 13.5% exact, 70.6% within-2")
log("    Mongolian, 500 pairs      9.5   ->  7.3% exact, 53.5% within-2")
log("    Sanskrit, 858 pairs       5.0   ->  8.8% exact, 39.2% within-2")
log(f"    THIS corpus             {tok/max(1,len(syl)):5.1f}")
log()
log("  But two things push this above the curve: the unit is a READING (Mandarin")
log("  has a closed syllable inventory, so obs/unit rises fast with more pairs),")
log("  and reading-anchoring was worth +16 points on exact match at Han-era")
log("  volume in step 11. Most importantly this is IN-DOMAIN Turkic, which is")
log("  precisely what step 11 lacked when it collapsed from 46% to 10%.")
log()
log(f"most frequent EFEO syllables:")
log("  " + "  ".join(f"{s}({n})" for s, n in syl.most_common(18)))
log()
log("SAMPLE - 18 extracted pairs:")
log(f"  {'turkic':22s} {'efeo chinese':24s} gloss")
for r in clean[:18]:
    log(f"  {r['turkic'][:22]:22s} {r['efeo_chinese'][:24]:24s} {r['gloss_fr'][:30]}")
log()

dst = os.path.join(DER, "ligeti_turkic_chinese_pairs.csv")
with open(dst, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["turkic","efeo_chinese","n_syllables",
                                      "gloss_fr","source","pdf_page","suspect"])
    w.writeheader(); w.writerows(uniq.values())
log(f"Written to data/derived/ligeti_turkic_chinese_pairs.csv ({len(uniq):,} rows)")
log()
log("CAVEAT: EFEO romanises a Mandarin reading, so this is Ming-era Chinese, not")
log("Later Han. Applying a channel trained here to the Xiongnu names still crosses")
log("~1,200 years of phonological change. That gap is now the ONLY one left, where")
log("before it was gap PLUS wrong source language PLUS wrong transcription")
log("convention. One problem instead of three.")

with open(os.path.join(REP, "step12_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\nSummary written to reports/step12_summary.txt")
