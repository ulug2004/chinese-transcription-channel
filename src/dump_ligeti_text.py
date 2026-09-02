#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dump the text of Ligeti's glossary sections to a single file.

Ligeti prints the Chinese transcription in EFEO romanisation, not characters:

    bitig (pi-ti) «livre (chou)» II 12a (72a)
    biz-lar (pi-sseu-la-eul) «nous» I 23b (45a)

That is a READING, which is exactly what the reading-anchored channel needs, so
the volumes are usable after all. This dumps the raw glossary text so the parser
can be written against the real formatting instead of guessed at.

Output: reports/ligeti_glossary_raw.txt  (a few hundred KB of plain text)
Needs pdfplumber.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL   = os.path.join(ROOT, "Downloads")
REP  = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)

try:
    import pdfplumber
except ImportError:
    print("ERROR: pip install pdfplumber"); sys.exit(1)

# Running heads. CRITICAL: journals put the article TITLE on recto (odd) pages
# and the AUTHOR NAME on verso (even) pages. An earlier version of this script
# listed only the title, so every even page was silently dropped - roughly half
# the article. "ligeti" must be here.
HEADS = ["vocabulaire sino-ouigour", "glossaire supplémentaire",
         "glossaire supplementaire", "sino-ouigour", "ligeti",
         "l. ligeti", "louis ligeti"]
# An entry line looks like:  headword (efeo-form) «gloss»
ENTRY = None

chunks, stats = [], []
for fn, tag in (("Ligeti_1966_ActaOrientalia_19.pdf", "L1966"),
                ("Ligeti_1969_ActaOrientalia_22.pdf", "L1969")):
    path = os.path.join(DL, fn)
    if not os.path.exists(path):
        print(f"  !! {fn} not found"); continue
    kept = 0
    with pdfplumber.open(path) as pdf:
        for i, pg in enumerate(pdf.pages):
            try: t = pg.extract_text() or ""
            except Exception: continue
            low = t.lower()
            head_ok = any(h in low for h in HEADS)
            # Some pages lose their running head to OCR. Keep any page that
            # carries the entry signature regardless: a parenthesised
            # lowercase-Latin form followed by a guillemet gloss.
            sig = bool(re.search(r'\([a-z\'\-]{2,}\)\s*[,.]?\s*«', t))
            if not (head_ok or sig): continue
            if t.count("«") < 1 and not sig: continue
            kept += 1
            chunks.append(f"\n===PAGE {tag} {i}===\n{t}")
    stats.append((fn, kept))
    print(f"  {fn}: kept {kept} glossary pages")

body = "".join(chunks)
outp = os.path.join(REP, "ligeti_glossary_raw.txt")
with open(outp, "w", encoding="utf-8") as f: f.write(body)
print(f"\nWrote {outp}  ({len(body):,} characters)")
print(f"  glossary-delimiter count: « x{body.count('«')}")
import re as _re
_n = len(_re.findall(r"\([a-z'\-]{2,}\)\s*[,.]?\s*«", body))
print(f"  entry-signature count (efeo-paren + gloss): {_n}")
