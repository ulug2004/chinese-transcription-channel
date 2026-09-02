#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Locate Ligeti's Sino-Uyghur vocabulary inside the Acta Orientalia volume PDFs,
and probe the Shi Shuqin report.

The volumes are whole years (~800 pages each), so the JOURNAL page numbers from
the citation (19: 117-199, 257-316) are not PDF page indices. This finds the real
indices and samples the layout, so the extractor can be written against the
actual format rather than guessed at.

Writes a small report to reports/probe_ligeti.txt. Stdlib + pdfplumber.
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
    print("ERROR: pdfplumber not installed.  pip install pdfplumber")
    sys.exit(1)

CJK = re.compile(r'[㐀-䶿一-鿿]')
# Ligeti's article titles and the running heads that mark the vocabulary itself
HINTS = ["sino-ouigour", "ouigour", "kao-tch", "bureau des traducteurs",
         "glossaire supplémentaire", "glossaire supplementaire", "ligeti"]

def probe_volume(fn, label, ranges):
    path = os.path.join(DL, fn)
    if not os.path.exists(path):
        w(f"  !! {fn} not found in Downloads/"); return
    w("=" * 70)
    w(f" {label}")
    w(f" {fn}  ({os.path.getsize(path):,} bytes)")
    w("=" * 70)
    w(f" citation page ranges: {ranges}")
    w()
    hits, printed_pages, cjk_pages = [], {}, []
    with pdfplumber.open(path) as pdf:
        n = len(pdf.pages)
        w(f" PDF pages: {n}")
        for i, pg in enumerate(pdf.pages):
            try: t = pg.extract_text() or ""
            except Exception: continue
            low = t.lower()
            if any(h in low for h in HINTS): hits.append(i)
            # printed page number, usually alone on the first or last line
            for ln in (t.split("\n") or [""])[:2] + (t.split("\n") or [""])[-2:]:
                m = re.fullmatch(r'\s*(\d{1,3})\s*', ln)
                if m: printed_pages[int(m.group(1))] = i; break
            if len(CJK.findall(t)) >= 15: cjk_pages.append(i)
        w(f" pages mentioning Ligeti / sino-ouigour: {len(hits)}")
        if hits: w(f"   first 25 PDF indices: {hits[:25]}")
        w(f" pages with >=15 Chinese characters: {len(cjk_pages)}")
        if cjk_pages:
            w(f"   range: PDF pages {cjk_pages[0]}-{cjk_pages[-1]}")
        w()
        # map the citation's journal pages onto PDF indices
        w(" journal page -> PDF index (from printed page numbers found):")
        for jp in [r for pair in ranges for r in pair]:
            if jp in printed_pages:
                w(f"   printed p.{jp:<4d} -> PDF page {printed_pages[jp]}")
            else:
                near = [p for p in sorted(printed_pages) if abs(p-jp) <= 3]
                w(f"   printed p.{jp:<4d} -> not detected"
                  + (f"; nearest found {near}" if near else ""))
        w()
        # sample the layout from a Chinese-bearing page inside the article
        target = None
        for i in cjk_pages:
            if hits and not (hits[0] - 5 <= i <= hits[-1] + 5): continue
            target = i; break
        if target is None and cjk_pages: target = cjk_pages[len(cjk_pages)//2]
        if target is not None:
            w("-" * 70)
            w(f" LAYOUT SAMPLE - PDF page {target}, first 30 lines")
            w("-" * 70)
            t = pdf.pages[target].extract_text() or ""
            for ln in [l for l in t.split("\n") if l.strip()][:30]:
                w("   " + ln[:150])
            w()
            w("-" * 70)
            w(f" WORD-COORDINATE SAMPLE - PDF page {target}, first 3 rows by x-position")
            w("-" * 70)
            ws = [x for x in pdf.pages[target].extract_words() if x["text"].strip()]
            for x in ws: x["mid"] = (x["top"]+x["bottom"])/2
            ws.sort(key=lambda x: (x["mid"], x["x0"]))
            rows, cur, last = [], [], None
            for x in ws:
                if last is None or abs(x["mid"]-last) <= 6: cur.append(x)
                else: rows.append(cur); cur=[x]
                last = x["mid"]
            if cur: rows.append(cur)
            for r in rows[:6]:
                w("   " + " | ".join(f'{x["text"]}@{int(x["x0"])}' for x in r)[:170])
    w()

w(" LIGETI / SINO-UYGHUR VOCABULARY - LOCATION PROBE")
w()
probe_volume("Ligeti_1966_ActaOrientalia_19.pdf",
             "Ligeti 1966, Acta Orientalia 19", [(117,199),(257,316)])
probe_volume("Ligeti_1969_ActaOrientalia_22.pdf",
             "Ligeti 1969, Acta Orientalia 22", [(1,49),(191,243)])

# ---- the small Chinese report ----
for cand in ("Shi_Shuqin_2016_gaochang_study.pdf", "84990619.pdf"):
    p = os.path.join(DL, cand)
    if not os.path.exists(p): continue
    w("=" * 70)
    w(f" Shi Shuqin 2016 report - {cand} ({os.path.getsize(p):,} bytes)")
    w("=" * 70)
    with pdfplumber.open(p) as pdf:
        w(f" pages: {len(pdf.pages)}")
        tables = 0; cjkheavy = []
        for i, pg in enumerate(pdf.pages):
            t = pg.extract_text() or ""
            if len(CJK.findall(t)) >= 40: cjkheavy.append(i)
        w(f" pages with >=40 Chinese characters: {len(cjkheavy)}")
        # look for an appendix / word-list section
        for i, pg in enumerate(pdf.pages):
            t = pg.extract_text() or ""
            if any(k in t for k in ("附录","附錄","词汇表","詞彙表","对照表","對照表")):
                w(f"   appendix / word-list marker on page {i}: "
                  + " / ".join(k for k in ("附录","附錄","词汇表","詞彙表","对照表","對照表") if k in t))
        mid = cjkheavy[len(cjkheavy)//2] if cjkheavy else 0
        w()
        w(f" SAMPLE - page {mid}, first 18 lines")
        t = pdf.pages[mid].extract_text() or ""
        for ln in [l for l in t.split("\n") if l.strip()][:18]:
            w("   " + ln[:140])
    w()

with open(os.path.join(REP, "probe_ligeti.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\nReport written to reports/probe_ligeti.txt")
