#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Probe the Secret History of the Mongols epub.

Writes a SMALL structural report to reports/probe_shm.txt so the extractor can be
written against the real format instead of guessed at. Deliberately compact -
the point is to look at the shape of the data, not to ship the data anywhere.

Stdlib only.
"""
import os, re, sys, zipfile, html
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL   = os.path.join(ROOT, "Downloads")
REP  = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)

CJK  = re.compile(r'[一-鿿㐀-䶿]')
LAT  = re.compile(r'[a-zA-Zäöüïğčšñŋəḳɣžǰāēīōūáéíóú]')
TAG  = re.compile(r'<[^>]+>')

out = []
def w(s=""):
    print(s); out.append(s)

# find the epub (any .epub in Downloads)
cands = [f for f in os.listdir(DL) if f.lower().endswith(".epub")] if os.path.isdir(DL) else []
if not cands:
    w("No .epub found in Downloads/. Nothing to probe.")
else:
    path = os.path.join(DL, cands[0])
    w("=" * 68)
    w(" SECRET HISTORY EPUB - structural probe")
    w("=" * 68)
    w(f"file: {cands[0]}  ({os.path.getsize(path):,} bytes)")
    w()
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        w(f"internal entries: {len(names)}")
        content = [n for n in names if n.lower().endswith((".xhtml",".html",".htm",".xml",".txt"))]
        content = [n for n in content if "nav" not in n.lower() and "toc" not in n.lower()]
        sizes = sorted(((z.getinfo(n).file_size, n) for n in content), reverse=True)
        w(f"content documents: {len(sizes)}   largest 12:")
        for sz, n in sizes[:12]:
            w(f"   {sz:9,}  {n}")
        w()

        def lines_of(n):
            raw = z.read(n).decode("utf-8", "replace")
            raw = re.sub(r'(?is)<(script|style).*?</\1>', ' ', raw)
            raw = re.sub(r'(?i)</(p|div|br|tr|td|li|h[1-6])\s*/?>', '\n', raw)
            raw = re.sub(r'(?i)<br\s*/?>', '\n', raw)
            txt = html.unescape(TAG.sub(' ', raw))
            return [re.sub(r'[ \t ]+', ' ', l).strip() for l in txt.split("\n")]

        # global stats: how many lines carry BOTH scripts (the alignment signal)
        tot = both = 0
        per_doc = []
        for sz, n in sizes[:40]:
            ls = lines_of(n)
            b = sum(1 for l in ls if l and CJK.search(l) and LAT.search(l))
            tot += sum(1 for l in ls if l); both += b
            per_doc.append((b, n))
        w(f"lines with BOTH Chinese and Latin script: {both} of {tot} non-empty lines")
        w("  (this is the alignment signal - if it is near zero the epub is")
        w("   romanisation-only and the ja.wikisource dump is needed instead)")
        w()
        per_doc.sort(reverse=True)
        w("richest documents by mixed-script line count:")
        for b, n in per_doc[:6]:
            w(f"   {b:6d}  {n}")
        w()

        # sample from the richest document
        if per_doc and per_doc[0][0] > 0:
            target = per_doc[0][1]
            ls = [l for l in lines_of(target) if l and CJK.search(l) and LAT.search(l)]
            w("-" * 68)
            w(f" SAMPLE - 25 mixed-script lines from {target}")
            w("-" * 68)
            for l in ls[:25]:
                w("   " + (l[:150] + (" ..." if len(l) > 150 else "")))
            w()
            w("-" * 68)
            w(" SAMPLE - 10 lines from the middle of the same document")
            w("-" * 68)
            mid = len(ls)//2
            for l in ls[mid:mid+10]:
                w("   " + (l[:150] + (" ..." if len(l) > 150 else "")))
            w()
            # what do CJK-only and Latin-only lines look like? (interleaved layout)
            allls = [l for l in lines_of(target) if l]
            w("-" * 68)
            w(" SAMPLE - 20 consecutive raw lines (to reveal interleaved layout)")
            w("-" * 68)
            start = next((i for i, l in enumerate(allls) if CJK.search(l) and LAT.search(l)), 0)
            for l in allls[start:start+20]:
                kind = ("BOTH" if CJK.search(l) and LAT.search(l)
                        else "CJK " if CJK.search(l) else "LAT " if LAT.search(l) else "----")
                w(f"   [{kind}] " + (l[:130] + (" ..." if len(l) > 130 else "")))
        else:
            w("!! No mixed-script lines found. Sampling raw lines from the largest doc:")
            ls = [l for l in lines_of(sizes[0][1]) if l][:25]
            for l in ls: w("   " + l[:150])

with open(os.path.join(REP, "probe_shm.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
print("\nReport written to reports/probe_shm.txt")
