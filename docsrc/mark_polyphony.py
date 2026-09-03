# -*- coding: utf-8 -*-
"""Mark, with a dagger, every printed Later Han syllable whose character has
more than one reading in Schuessler's table. Operates on the appendix and
comparison tables of paper.html, which pair a han2 cell with a num cell."""
import csv, io, re, sys, collections

LHTAB = "/mnt/user-data/uploads/claude/names/data/external/LHantab.tsv"

def polyset():
    n = collections.Counter()
    with io.open(LHTAB, encoding="utf8", errors="ignore") as f:
        seen = set()
        for x in csv.DictReader(f, delimiter="\t"):
            z = (x.get("zi") or "").strip()
            syl = (x.get("syl_bok") or "").strip()
            if z and syl and (z, syl) not in seen:
                seen.add((z, syl)); n[z] += 1
    return {z for z, k in n.items() if k > 1}

DAG = '<span class="poly">†</span>'
CELL = re.compile(
    r'(<td class="han2"[^>]*>)([㐀-鿿]+)(<span class="py">.*?</td>\s*'
    r'<td class="num"[^>]*>)([^<]+)(</td>)', re.S)

def main(path):
    POLY = polyset()
    s = io.open(path, encoding="utf8").read()
    stats = collections.Counter()
    def sub(m):
        a, chars, b, reading, c = m.groups()
        syls = reading.split()
        if len(syls) != len(chars):
            stats["skipped"] += 1
            return m.group(0)
        out = []
        for ch, sy in zip(chars, syls):
            if ch in POLY:
                out.append(sy + DAG); stats["marked"] += 1
            else:
                out.append(sy)
        stats["rows"] += 1
        return a + chars + b + " ".join(out) + c
    s2 = CELL.sub(sub, s)
    if DAG not in s2:
        sys.exit("nothing marked")
    io.open(path, "w", encoding="utf8").write(s2)
    print("rows marked: %d   syllables daggered: %d   rows skipped (misaligned): %d"
          % (stats["rows"], stats["marked"], stats["skipped"]))

main(sys.argv[1])
