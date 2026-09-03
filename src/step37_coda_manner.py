# -*- coding: utf-8 -*-
"""
Step 37.  The full coda matrix: what does a written coda claim about the
source consonant, by place and by manner.

Step 34 asked two questions of this matrix (does a written coda switch
place, is a source nasal ever written as a stop).  Reading MAO-TUN needs
more cells than that, because the second character has three values on
offer and each candidate reading needs a different one of them:

    TUN row 1  *tuen   nasal coda
    TUN row 2  *tuet   dental stop coda
    TUN, the commentarial substitution recorded as TUN yin DU,
               velar stop coda  (not a row of the Later Han table)

against source finals  -n (tin),  -g (tug),  -r (bagatur).

So the script prints the whole matrix once and every cell any of those
readings needs is then a number rather than an assertion.

Alignment: the k-th character is paired with the k-th source vowel, and
the source coda is taken by the maximal-onset rule, a single consonant
between two vowels belonging to the following syllable.  Pairs whose
character count and vowel count disagree are dropped.
"""
import csv, os, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
OUT  = os.path.join(ROOT, "reports")

def rd(path, delim=","):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=delim))

SKT_V = ["ai", "au", "ā", "ī", "ū", "ṝ", "ṛ", "ḷ", "a", "i", "u", "e", "o"]
CODA_CH = "ktpnmŋ"

def lh_first():
    out = {}
    for row in rd(os.path.join(EXT, "LHantab.tsv"), "\t"):
        zi = (row.get("zi") or "").strip()
        vw = (row.get("vow") or "").strip()
        if zi and vw and zi not in out:
            out[zi] = vw
    return out

def written_coda(vow):
    m = re.search(r"[%s]+$" % CODA_CH, vow)
    return m.group(0) if m else ""

W_PLACE = {"k": "velar", "ŋ": "velar", "t": "dental", "n": "dental",
           "p": "labial", "m": "labial"}
W_MANNER = {"k": "stop", "t": "stop", "p": "stop",
            "ŋ": "nasal", "n": "nasal", "m": "nasal"}
def w_class(c):
    if not c:
        return "open"
    last = c[-1]
    return "%s %s" % (W_PLACE.get(last, "?"), W_MANNER.get(last, "?"))

# source side ------------------------------------------------------------
S_CLASS = {
    "k": "velar stop", "g": "velar stop", "kh": "velar stop", "gh": "velar stop",
    "c": "palatal", "j": "palatal", "ch": "palatal", "jh": "palatal",
    "t": "dental stop", "d": "dental stop", "th": "dental stop", "dh": "dental stop",
    "ṭ": "dental stop", "ḍ": "dental stop", "ṭh": "dental stop", "ḍh": "dental stop",
    "p": "labial stop", "b": "labial stop", "ph": "labial stop", "bh": "labial stop",
    "ṅ": "velar nasal", "ñ": "palatal nasal", "ṇ": "dental nasal",
    "n": "dental nasal", "m": "labial nasal", "ṃ": "labial nasal",
    "y": "glide", "v": "glide",
    "r": "liquid", "l": "liquid", "ḥ": "h", "h": "h",
    "ś": "sibilant", "ṣ": "sibilant", "s": "sibilant",
}
CONS = ["kh","gh","ch","jh","ṭh","ḍh","th","dh","ph","bh",
        "ṅ","ñ","ṇ","ṃ","ś","ṣ","ṭ","ḍ","ḥ",
        "k","g","c","j","t","d","p","b","n","m","y","r","l","v","s","h"]

def parse(word):
    """-> list of (vowel, coda_string) in order."""
    w = word.lower().strip()
    units, i, pend = [], 0, []
    while i < len(w):
        for v in SKT_V:
            if w.startswith(v, i):
                units.append([v, [], pend]); pend = []
                i += len(v); break
        else:
            for c in CONS:
                if w.startswith(c, i):
                    pend.append(c); i += len(c); break
            else:
                i += 1
    if units:
        units[-1][1] = pend          # word-final consonants are all coda
        pend = []
    out = []
    for k, (v, tail, before) in enumerate(units):
        if k + 1 < len(units):
            nxt = units[k + 1][2]     # consonants between this vowel and next
            coda = nxt[:-1] if len(nxt) >= 2 else []
        else:
            coda = tail
        out.append((v, coda))
    return out

def s_class(coda):
    if not coda:
        return "open"
    return S_CLASS.get(coda[-1], "other")

def main():
    lh = lh_first()
    pairs = rd(os.path.join(DER, "nti_transcription_pairs.csv"))
    tally = collections.Counter()
    kept = dropped = 0
    for row in pairs:
        chars = [c for c in (row.get("trad") or "") if "㐀" <= c <= "鿿"]
        units = parse(row.get("skt") or "")
        if not chars or len(chars) != len(units):
            dropped += 1
            continue
        kept += 1
        for ch, (v, coda) in zip(chars, units):
            vw = lh.get(ch)
            if not vw:
                continue
            tally[(s_class(coda), w_class(written_coda(vw)))] += 1

    lines = []
    def say(s=""):
        print(s); lines.append(s)

    say("Step 37.  Source coda class against written coda class,")
    say("Later Han layer, %d pairs used, %d dropped." % (kept, dropped))
    cols = ["open", "velar stop", "velar nasal", "dental stop",
            "dental nasal", "labial stop", "labial nasal"]
    cols = [c for c in cols if any(b == c for _, b in tally)]
    srcs = ["open", "velar stop", "velar nasal", "dental stop", "dental nasal",
            "labial stop", "labial nasal", "liquid", "sibilant", "palatal",
            "palatal nasal", "glide", "h", "other"]
    w = 14
    say("")
    say("  " + "source".ljust(15) + "".join(c.rjust(w) for c in cols) + "total".rjust(8))
    for s in srcs:
        n = sum(v for (a, b), v in tally.items() if a == s)
        if not n:
            continue
        line = "  " + s.ljust(15)
        for c in cols:
            v = tally.get((s, c), 0)
            line += ("%d (%.0f%%)" % (v, 100.0 * v / n)).rjust(w)
        say(line + str(n).rjust(8))

    def cell(s, c):
        n = sum(v for (a, b), v in tally.items() if a == s)
        return tally.get((s, c), 0), n
    say("")
    say("The cells the second character of MAO-TUN needs:")
    for label, s, c in [
        ("source -n  written as a dental nasal  (tin, TUN row 1)", "dental nasal", "dental nasal"),
        ("source -n  written as a dental stop   (tin, TUN row 2)", "dental nasal", "dental stop"),
        ("source -n  written as a velar stop    (tin, substitution)", "dental nasal", "velar stop"),
        ("source -g  written as a dental nasal  (tug, TUN row 1)", "velar stop", "dental nasal"),
        ("source -g  written as a dental stop   (tug, TUN row 2)", "velar stop", "dental stop"),
        ("source -g  written as a velar stop    (tug, substitution)", "velar stop", "velar stop"),
        ("source -r  written as a dental nasal  (bagatur, TUN row 1)", "liquid", "dental nasal"),
        ("source -r  written as a dental stop   (bagatur, TUN row 2)", "liquid", "dental stop"),
        ("source -r  written as a velar stop    (bagatur, substitution)", "liquid", "velar stop"),
    ]:
        k, n = cell(s, c)
        say("  %-58s %4d of %4d  %5.1f%%" % (label, k, n, 100.0 * k / n if n else 0))

    say("")
    say("Controls, the two questions step 34 asked:")
    k = sum(v for (a, b), v in tally.items()
            if a.endswith("nasal") and b.endswith("stop"))
    n = sum(v for (a, b), v in tally.items() if a.endswith("nasal"))
    say("  a source nasal written with a stop coda      %4d of %4d  %5.1f%%"
        % (k, n, 100.0 * k / n if n else 0))
    k = sum(v for (a, b), v in tally.items()
            if a.endswith("stop") and b.endswith("nasal"))
    n = sum(v for (a, b), v in tally.items() if a.endswith("stop"))
    say("  a source stop written with a nasal coda      %4d of %4d  %5.1f%%"
        % (k, n, 100.0 * k / n if n else 0))
    k = sum(v for (a, b), v in tally.items()
            if a.split()[0] in ("velar", "dental", "labial")
            and b.split()[0] in ("velar", "dental", "labial")
            and a.split()[0] != b.split()[0])
    n = sum(v for (a, b), v in tally.items()
            if a.split()[0] in ("velar", "dental", "labial")
            and b.split()[0] in ("velar", "dental", "labial"))
    say("  a written coda that switches place           %4d of %4d  %5.1f%%"
        % (k, n, 100.0 * k / n if n else 0))

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    with open(os.path.join(OUT, "step37_summary.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    main()
