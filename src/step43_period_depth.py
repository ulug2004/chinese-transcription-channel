# -*- coding: utf-8 -*-
"""
Step 43.  How far apart are the two reconstructions of the record's
characters, and does the gap change what a character could write?

The Xiongnu names are recorded in the Shiji and the Hanshu for events of
the third to the first century BCE.  Appendix A prices every one of them
against Schuessler's Later Han table, which describes Chinese of the first
and second centuries CE, one to three hundred years later.  For most
characters that gap is notational.  For some it is not: the segment class
the character carries is different, and a character that carries a velar
can write things a character that carries a glide cannot.

This measures how often that happens across the 107 characters of the
record, comparing Schuessler's Later Han against Baxter and Sagart's Old
Chinese, which is the other reconstruction the paper already cites.

Two honest limits, stated here because they bound what the number means.
Baxter and Sagart reconstruct a stage around the early Zhou, centuries
BEFORE the transcriptions, and Schuessler a stage centuries after, so the
transcriptions sit between the two and this measures the width of the
bracket rather than the value inside it.  And their *-s and *-ʔ are held
to have become tones by the Han, so they are stripped here and not counted
as codas.

Sources
  data\\external\\LHantab.tsv                      Schuessler, Later Han
  reports\\_textcache\\BaxterSagart_*_by_radical_stroke*.txt
      the extracted table, written by step 42's cache; if it is missing,
      run RUN-search-form.bat once and it will appear.

Output: reports\\step43_summary.txt, data\\derived\\period_depth.csv
"""
import csv, io, os, re, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
OUT  = os.path.join(ROOT, "reports")
CACHE = os.path.join(OUT, "_textcache")

# ---------------------------------------------------------------- classes
VELAR = set("kgŋqɢxɣhʁχ")
DENT  = set("tdnsz")
LAB   = set("pbmf")
PAL   = set("cjńśźɕʑ")
LIQ   = set("lr")
GLIDE = set("wjy")

def onset_class(c):
    c = (c or "").strip()
    if not c:
        return "zero"
    if c[0] == "ʔ":
        return "glottal"
    two = c[:2]
    if two in ("tś", "dź", "tsy", "dzy", "ny"):
        return "palatal"
    if two in ("ts", "dz"):
        return "dental"
    b = c[0]
    if b in "ṭḍṇṣ":            # retroflex, a dental series
        return "dental"
    if b in "śźɕʑ":
        return "palatal"
    if b == "l\u0325":
        return "liquid"
    if b in VELAR: return "velar"
    if b in PAL:   return "palatal"
    if b in DENT:  return "dental"
    if b in LAB:   return "labial"
    if b in LIQ:   return "liquid"
    if b in GLIDE: return "glide"
    return "other:" + b

def coda_class(k):
    k = (k or "").strip()
    if not k:
        return "open"
    m = {"k": "velar stop", "ŋ": "velar nasal", "t": "dental stop",
         "n": "dental nasal", "p": "labial stop", "m": "labial nasal",
         "r": "liquid", "l": "liquid", "g": "velar stop", "d": "dental stop",
         "b": "labial stop"}
    return m.get(k[-1], "other:" + k[-1])

# ------------------------------------------------------------- Later Han
def later_han():
    out = {}
    with io.open(os.path.join(EXT, "LHantab.tsv"), encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            z = (r.get("zi") or "").strip()
            if not z or z in out:
                continue
            con = (r.get("con") or "").strip()
            vow = (r.get("vow") or "").strip()
            m = re.search(r"[ktpnmŋ]+$", vow)
            out[z] = (con, m.group(0) if m else "", con + vow)
    return out

# --------------------------------------------------------- Baxter-Sagart
PRE = re.compile(r"^(?:[A-Za-zəɢʔ]{1,2}[.\u2010\-])+")
def bs_table():
    hits = sorted(glob.glob(os.path.join(CACHE, "BaxterSagart*radical*stroke*.txt")))
    if not hits:
        return {}
    t = io.open(hits[0], encoding="utf-8", errors="replace").read()
    parts = re.split(r"U\+([0-9A-Fa-f]{4,5})", t)
    out = {}
    for i in range(1, len(parts) - 1, 2):
        body, cp = parts[i - 1], parts[i]
        try:
            ch = chr(int(cp, 16))
        except ValueError:
            continue
        m = re.search(r"\*([^\s]+)", body)
        if not m:
            continue
        oc = m.group(1)
        out.setdefault(ch, []).append(oc)
    return out

def bs_parse(oc):
    """-> (onset string, coda string) from a Baxter-Sagart Old Chinese form"""
    s = oc.replace("\u04d9", "\u0259")   # the OCR doubles the schwa
    s = re.sub("\u0259{2,}", "\u0259", s)
    s = re.sub(r"\(<.*$", "", s)          # drop "(< *...)"
    s = s.replace("<r>", "").replace("(r)", "")
    s = s.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
    s = re.sub(r"[-‑]s$", "", s)          # the *-s suffix became a tone
    s = s.rstrip("ʔ")                     # the *-ʔ suffix became a tone
    s = PRE.sub("", s)                    # strip pre-initials: C., m-, s-, ...
    s = s.replace("ˤ", "").replace("ʷ", "").replace("ʰ", "")
    V = "aeiouəAEIOUAɨ"
    m = re.match(r"^([^%s]*)" % V, s)
    onset = m.group(1) if m else ""
    rest = s[len(onset):]
    # *-j and *-w are the offglides of a diphthong, not consonantal codas
    rest = re.sub(r"[jw]+$", "", rest)
    m2 = re.search(r"([^%s]+)$" % V, rest)
    coda = m2.group(1) if m2 else ""
    return onset, coda

def main():
    lh = later_han()
    bs = bs_table()
    lines = []
    def say(s=""):
        print(s); lines.append(s)

    if not bs:
        say("The Baxter-Sagart table is not in reports\\_textcache.")
        say("Run RUN-search-form.bat once (any form) and it will be cached,")
        say("then run this again.")
        return

    # the record's characters
    chars = []
    with io.open(os.path.join(DER, "author_proposals.csv"), encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            for c in (r.get("chinese") or ""):
                if "㐀" <= c <= "鿿" and c not in chars:
                    chars.append(c)

    say("Step 43.  Later Han against Old Chinese, over the record's characters.")
    say("Baxter and Sagart table: %d characters parsed." % len(bs))
    say("The record: %d distinct characters." % len(chars))
    say("")

    rows = []
    tally = collections.Counter()
    for ch in chars:
        if ch not in lh:
            tally["not in Schuessler's table"] += 1
            continue
        if ch not in bs:
            tally["not in Baxter and Sagart"] += 1
            continue
        con, k, full = lh[ch]
        lo, lk = onset_class(con), coda_class(k)
        # a character can have several OC readings; keep the one that differs
        # least, so the count is a floor rather than a ceiling
        best = None
        for oc in bs[ch]:
            o, c = bs_parse(oc)
            bo, bk = onset_class(o), coda_class(c)
            score = (bo != lo) + (bk != lk)
            if best is None or score < best[0]:
                best = (score, oc, bo, bk)
        score, oc, bo, bk = best
        verdict = ("same" if score == 0 else
                   ("onset and coda" if score == 2 else
                    ("onset" if bo != lo else "coda")))
        tally[verdict] += 1
        rows.append({"char": ch, "later_han": full, "old_chinese": oc,
                     "lh_onset": lo, "oc_onset": bo,
                     "lh_coda": lk, "oc_coda": bk, "differs_in": verdict})

    n = sum(v for k, v in tally.items() if k in ("same", "onset", "coda", "onset and coda"))
    say("Of the %d characters present in both reconstructions:" % n)
    for k in ("same", "onset", "coda", "onset and coda"):
        if tally[k]:
            say("   %-16s %3d   %5.1f%%" % (k, tally[k], 100.0 * tally[k] / n))
    for k in ("not in Schuessler's table", "not in Baxter and Sagart"):
        if tally[k]:
            say("   (%s: %d)" % (k, tally[k]))
    diff = tally["onset"] + tally["coda"] + tally["onset and coda"]
    say("")
    say("   a different class of segment in one position or both:"
        "  %d of %d,  %.0f%%" % (diff, n, 100.0 * diff / n))
    say("")
    say("The characters where it differs, and how")
    say("  %-4s %-12s %-14s %-22s %s" % ("", "Later Han", "Old Chinese", "onset", "coda"))
    for r in sorted(rows, key=lambda r: r["differs_in"]):
        if r["differs_in"] == "same":
            continue
        say("  %-4s %-12s %-14s %-22s %s"
            % (r["char"], r["later_han"], r["old_chinese"],
               "%s -> %s" % (r["lh_onset"], r["oc_onset"]) if r["lh_onset"] != r["oc_onset"] else "",
               "%s -> %s" % (r["lh_coda"], r["oc_coda"]) if r["lh_coda"] != r["oc_coda"] else ""))

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    io.open(os.path.join(OUT, "step43_summary.txt"), "w",
            encoding="utf-8").write("\n".join(lines) + "\n")
    if rows:
        p = os.path.join(DER, "period_depth.csv")
        with io.open(p, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        print(""); print("written: " + p)
    print("written: " + os.path.join(OUT, "step43_summary.txt"))

if __name__ == "__main__":
    main()
