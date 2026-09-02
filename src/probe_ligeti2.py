#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Follow-up probe: is Ligeti's Chinese column recoverable?

The first probe found ZERO extractable Chinese characters in both Acta volumes.
That is decisive if true - Ligeti's entries pair Chinese transcription characters
with romanised Uyghur, and without the Chinese side the pairs are useless here.

Two possibilities:
  (a) the Chinese glyphs are in the page IMAGE but the 1966/69 OCR was Latin-only
      -> recoverable with a CJK OCR pass
  (b) Ligeti gives no Chinese characters at all, only romanisation
      -> the volumes cannot supply what we need, full stop

This locates the vocabulary body, dumps its Latin text, and RENDERS two pages to
PNG so the images can be inspected directly. That settles (a) vs (b).

Needs pdfplumber and pypdfium2 (pip install pypdfium2).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL   = os.path.join(ROOT, "Downloads")
REP  = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)
out = []
def w(s=""):
    print(s); out.append(s)

try:
    import pdfplumber
except ImportError:
    print("ERROR: pip install pdfplumber"); sys.exit(1)
HAVE_RENDER = True
try:
    import pypdfium2 as pdfium
except ImportError:
    HAVE_RENDER = False

TITLE_HINTS = ["vocabulaire sino-ouigour", "kao-tch", "bureau des traducteurs",
               "glossaire suppl"]
BODY_HINTS  = ["sino-ouigour", "ouigour"]

def handle(fn, label, npages_dump=3, render=(0,1)):
    path = os.path.join(DL, fn)
    if not os.path.exists(path):
        w(f"  !! {fn} not in Downloads/"); return
    w("=" * 70); w(f" {label}"); w("=" * 70)
    with pdfplumber.open(path) as pdf:
        n = len(pdf.pages)
        texts = []
        for i, pg in enumerate(pdf.pages):
            try: texts.append(pg.extract_text() or "")
            except Exception: texts.append("")
        # find the article start: a page whose text contains a title hint
        starts = [i for i,t in enumerate(texts)
                  if any(h in t.lower() for h in TITLE_HINTS)]
        body = [i for i,t in enumerate(texts)
                if any(h in t.lower() for h in BODY_HINTS)]
        w(f" pages: {n}   title-hint pages: {starts[:12]}")
        if body: w(f" body-hint span: {body[0]}..{body[-1]} ({len(body)} pages)")
        # pick pages that look like DENSE ENTRY LISTS: many short lines
        def density(t):
            ls=[l for l in t.split("\n") if l.strip()]
            if len(ls) < 12: return 0
            short=sum(1 for l in ls if len(l) < 60)
            return short
        cand = sorted(((density(texts[i]), i) for i in (body or range(n))), reverse=True)
        picks = [i for _,i in cand[:npages_dump]]
        w(f" densest entry-list pages: {picks}")
        w()
        for i in picks:
            w("-" * 70)
            w(f" TEXT DUMP - PDF page {i} (first 28 non-empty lines)")
            w("-" * 70)
            for l in [x for x in texts[i].split("\n") if x.strip()][:28]:
                w("   " + l[:150])
            w()
        # character inventory across the body - what scripts did OCR see?
        allt = "".join(texts[i] for i in (body or range(min(n,80))))
        cjk = sum(1 for c in allt if '㐀' <= c <= '鿿')
        latin = sum(1 for c in allt if c.isascii() and c.isalpha())
        other = sorted({c for c in allt if ord(c) > 0x2000 and not ('㐀' <= c <= '鿿')})
        w(f" OCR character inventory over the body: latin {latin:,}  CJK {cjk:,}")
        w(f" non-ASCII non-CJK symbols seen: {''.join(other[:60])}")
        w()
        if HAVE_RENDER:
            doc = pdfium.PdfDocument(path)
            for k, off in enumerate(render):
                idx = picks[off] if off < len(picks) else picks[0]
                pil = doc[idx].render(scale=150/72).to_pil()
                fp = os.path.join(REP, f"ligeti_page_{label.split()[1].strip(',')}_{idx}.png")
                pil.save(fp)
                w(f" rendered PDF page {idx} -> reports/{os.path.basename(fp)} "
                  f"({os.path.getsize(fp):,} bytes)")
            doc.close()
        else:
            w(" !! pypdfium2 not installed - no page images rendered.")
            w("    Install with:  pip install pypdfium2   then re-run.")
    w()

handle("Ligeti_1966_ActaOrientalia_19.pdf", "Ligeti 1966, vol 19")
handle("Ligeti_1969_ActaOrientalia_22.pdf", "Ligeti 1969, vol 22")

with open(os.path.join(REP, "probe_ligeti2.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\nReport written to reports/probe_ligeti2.txt")
