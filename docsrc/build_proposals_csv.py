# -*- coding: utf-8 -*-
"""
build_proposals_csv.py -- regenerate the note column of author_proposals.csv
from s1_rows.py, so the released CSV and the supplement cannot disagree.

The note column had drifted badly: of 40 rows, 13 were empty, 6 matched the
supplement, and 21 held older or shorter text. s1_rows.py is the maintained
source for that prose, so the note is now derived from it: the phonetics
remark followed by the reason remark, tags stripped.

Every other column is left exactly as it is; this script only rewrites `note`.
"""
import csv, io, re, sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from s1_rows import REMARK

def plain(h):
    h = re.sub(r"<br\s*/?>", " ", h)
    h = re.sub(r"<[^>]+>", "", h)
    return re.sub(r"\s+", " ", h).strip()

P = "author_proposals.csv"
rows = list(csv.DictReader(io.open(P, encoding="utf-8-sig")))
fields = list(rows[0].keys())
missing = [r["chinese"] for r in rows if r["chinese"] not in REMARK]
if missing:
    sys.exit("not in s1_rows.py: %s" % missing)

changed = 0
for r in rows:
    ph, rs = REMARK[r["chinese"]]
    new = plain(ph) + " " + plain(rs)
    if (r.get("note") or "").strip() != new:
        r["note"] = new; changed += 1
    else:
        r["note"] = new

with io.open(P, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(rows)
print("rows: %d   note column rewritten: %d" % (len(rows), changed))
blank = [r["chinese"] for r in rows if not (r.get("note") or "").strip()]
print("rows still without a note: %s" % (blank or "none"))
