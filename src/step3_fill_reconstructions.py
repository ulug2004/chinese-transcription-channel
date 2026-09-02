#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 3 - fill the PENDING reconstruction columns in the Xiongnu CSVs.

Joins each Chinese character in data/*.csv against Schuessler's Later Han
(LHantab.tsv) and Minimal Old Chinese (OCMtab.tsv) tables.

IMPORTANT: the per-name string this produces is a MECHANICAL CONCATENATION of
per-character readings. It is not a reconstruction of the name. Chinese
transcription involves cluster simplification, coda deletion and epenthesis, so
the real source form is not the concatenation. Treat this as the INPUT to the
channel model, not its output.

Stdlib only. Writes to data/derived/ and reports/.
"""
import csv, os, re, sys, zipfile, unicodedata
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT  = os.path.join(ROOT, "data", "external")
DATA = os.path.join(ROOT, "data")
OUT  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
for d in (OUT, REP): os.makedirs(d, exist_ok=True)

CJK = re.compile(r'[㐀-䶿一-鿿豈-﫿]')
log_lines = []
def log(s=""):
    print(s)
    log_lines.append(s)

# --------------------------------------------------------------- variants
# Schuessler's tables mix character forms (they use 虚 撐 户 脱 禄 where the
# histories print 虛 撑 戶 脫 祿). Without this, ~15% of lookups miss silently.
def load_variants():
    """Build char -> {equivalent chars} from Unihan_Variants.txt inside Unihan.zip."""
    zp = os.path.join(EXT, "Unihan.zip")
    eq = defaultdict(set)
    if not os.path.exists(zp):
        log("  !! Unihan.zip not found - variant resolution disabled")
        return eq
    FIELDS = {"kSemanticVariant", "kZVariant", "kSimplifiedVariant",
              "kTraditionalVariant", "kSpecializedSemanticVariant"}
    try:
        with zipfile.ZipFile(zp) as z:
            name = next((n for n in z.namelist() if n.endswith("Unihan_Variants.txt")), None)
            if not name:
                log("  !! Unihan_Variants.txt not inside Unihan.zip"); return eq
            for raw in z.open(name):
                line = raw.decode("utf-8", "replace")
                if line.startswith("#") or not line.strip(): continue
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 3: continue
                cp, field, val = parts[0], parts[1], parts[2]
                if field not in FIELDS: continue
                try: a = chr(int(cp[2:], 16))
                except Exception: continue
                for tok in val.split():
                    m = re.match(r"U\+([0-9A-Fa-f]+)", tok)
                    if not m: continue
                    b = chr(int(m.group(1), 16))
                    eq[a].add(b); eq[b].add(a)
    except Exception as e:
        log(f"  !! could not read Unihan.zip ({e}) - variant resolution disabled")
        return defaultdict(set)
    log(f"  Unihan variants: {len(eq)} characters have at least one equivalent form")
    return eq

VARIANTS = None   # set after EXT is known

def lookup(tbl, c):
    """Table lookup with variant and normalisation fallback.
       Returns (readings, resolved_char) or (None, None)."""
    if c in tbl: return tbl[c], c
    for form in (unicodedata.normalize("NFC", c), unicodedata.normalize("NFKC", c)):
        if form != c and form in tbl: return tbl[form], form
    for v in sorted(VARIANTS.get(c, ())):
        if v in tbl: return tbl[v], v
    return None, None

def load_table(path, name):
    """Read a Schuessler TSV. Returns {char: [readings]} and a note on columns."""
    if not os.path.exists(path):
        log(f"  !! {name}: NOT FOUND at {path}")
        return {}, None
    with open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    if not rows:
        log(f"  !! {name}: file is empty")
        return {}, None
    hdr = [h.strip() for h in rows[0]]
    # locate the character column and the reconstruction column
    char_i = None
    for cand in ("zi", "id", "char", "graph"):
        if cand in hdr: char_i = hdr.index(cand); break
    if char_i is None: char_i = 0
    rec_i = None
    for cand in ("syl_bok", "syl", "recon", "reconstruction", "form", "OCM", "ocm", "LHan", "lhan"):
        if cand in hdr: rec_i = hdr.index(cand); break
    if rec_i is None:
        # fall back to the last column that is not obviously an id
        rec_i = len(hdr) - 1
    d = defaultdict(list)
    for r in rows[1:]:
        if len(r) <= max(char_i, rec_i): continue
        c = r[char_i].strip()
        v = r[rec_i].strip()
        if not c or not v: continue
        # the char column sometimes holds a multi-char id; keep single graphs only
        if len(c) != 1: continue
        if v not in d[c]: d[c].append(v)
    log(f"  {name}: {len(rows)-1} rows -> {len(d)} distinct characters "
        f"(char col '{hdr[char_i]}', reading col '{hdr[rec_i]}')")
    return d, hdr

log("=" * 62)
log(" STEP 3 - fill reconstruction columns")
log("=" * 62)
log()
log("Loading Schuessler tables:")
LHAN, lhdr = load_table(os.path.join(EXT, "LHantab.tsv"), "LHantab (Later Han)")
OCM,  ohdr = load_table(os.path.join(EXT, "OCMtab.tsv"),  "OCMtab (Minimal Old Chinese)")
VARIANTS = load_variants()
if not LHAN:
    log("\nFATAL: LHantab.tsv could not be read. Nothing to join against.")
    sys.exit(1)
log()

miss_lhan = defaultdict(int)
miss_ocm  = defaultdict(int)
via_variant = {}

def annotate(chinese):
    """Return (lhan_join, lhan_detail, lhan_cov, ocm_join, ocm_detail, ocm_cov)."""
    chars = CJK.findall(chinese or "")
    if not chars: return ("", "", "0/0", "", "", "0/0")
    def do(tbl, missbin):
        parts, detail, found = [], [], 0
        for c in chars:
            rs, resolved = lookup(tbl, c)
            if rs:
                found += 1
                parts.append(rs[0])
                if resolved != c:
                    via_variant[c] = resolved
                    detail.append(f"{c}[={resolved}]={'|'.join(rs)}")
                else:
                    detail.append(f"{c}={'|'.join(rs)}")
            else:
                parts.append("?")
                detail.append(f"{c}=?")
                missbin[c] += 1
        return " ".join(parts), " ; ".join(detail), f"{found}/{len(chars)}"
    lj, ld, lc = do(LHAN, miss_lhan)
    oj, od, oc = do(OCM, miss_ocm)
    return lj, ld, lc, oj, od, oc

def process(fname):
    src = os.path.join(DATA, fname)
    if not os.path.exists(src):
        log(f"  !! {fname} not found - skipped")
        return None
    with open(src, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        log(f"  !! {fname} is empty"); return None
    newcols = ["lhan_detail", "lhan_coverage", "ocm_naive_join", "ocm_detail", "ocm_coverage"]
    fields = list(rows[0].keys())
    for c in newcols:
        if c not in fields: fields.append(c)
    full = partial = none_ = 0
    for r in rows:
        lj, ld, lc, oj, od, oc = annotate(r.get("chinese", ""))
        r["lhan_schuessler"] = lj or "NOT_FOUND"
        r["lhan_detail"]     = ld
        r["lhan_coverage"]   = lc
        r["ocm_naive_join"]  = oj
        r["ocm_detail"]      = od
        r["ocm_coverage"]    = oc
        if lj and "?" not in lj:
            r["verification_status"] = "AUTO_JOINED_LHAN"
            full += 1
        elif lj and lj.strip("? "):
            r["verification_status"] = "AUTO_JOINED_PARTIAL"
            partial += 1
        else:
            none_ += 1
    dst = os.path.join(OUT, fname.replace(".csv", "_reconstructed.csv"))
    with open(dst, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    log(f"  {fname}: {len(rows)} rows -> all chars found: {full}, partial: {partial}, none: {none_}")
    log(f"      written: data/derived/{os.path.basename(dst)}")
    return rows

log("Joining:")
r1 = process("xiongnu_rulers.csv")
r2 = process("xiongnu_titles_lexicon.csv")
log()

if via_variant:
    log(f"Resolved through a variant form ({len(via_variant)}):")
    log("  " + "  ".join(f"{a}->{b}" for a, b in sorted(via_variant.items())))
    log()
for label, bin_ in (("Later Han", miss_lhan), ("Old Chinese", miss_ocm)):
    if bin_:
        log(f"Still missing from {label} ({len(bin_)} distinct):")
        log("  " + "  ".join(f"{c}({n})" for c, n in
            sorted(bin_.items(), key=lambda x: -x[1])))
    else:
        log(f"Still missing from {label}: none - full coverage")
log()

# ---- show the headline items ----
log("-" * 62)
log(" Key items in Later Han (mechanical per-character join)")
log("-" * 62)
WANT = ["頭曼","冒頓","攣鞮","虛連題","呼韓邪","郅支",
        "單于","撑犁","孤塗","屠耆","閼氏","匈奴","羯"]
index = {}
for rows in (r1 or [], r2 or []):
    for r in rows: index[r.get("chinese","")] = r
for w in WANT:
    r = index.get(w)
    if not r: continue
    gloss = (r.get("proposed_reading") or "").strip()
    note  = f"   [proposed: {gloss}]" if gloss else ""
    log(f"  {w:8s} {r.get('pinyin_modern',''):22s} {r.get('lhan_schuessler','')}{note}")
log()
log("REMINDER: the above is a per-character concatenation, NOT a reconstruction")
log("of the name. Transcription deletes codas, simplifies clusters and inserts")
log("vowels. This is the model's INPUT, not its answer.")
log()

with open(os.path.join(REP, "step3_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines) + "\n")
print(f"\nSummary written to reports/step3_summary.txt")
