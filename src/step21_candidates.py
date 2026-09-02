# -*- coding: utf-8 -*-
"""
step21_candidates.py  -- build the permitted candidate space for every proposed name.

For each row of data/derived/author_proposals.csv this takes the Later Han reading,
expands it into the set of Turkic consonant skeletons that the step-15 initial
correspondences permit, and lists every headword in the Dīwān and the Codex Cumanicus
whose own skeleton matches. Each candidate is then checked against the Clauson EPUB.

The point is to do the searching locally and once, so that only the judgement has to
happen in conversation. Output: data/derived/name_candidates.csv

Usage:   python step21_candidates.py            all names
         python step21_candidates.py 且渠        one name (substring match on the Chinese)

Stdlib only. No network.
"""
import csv, io, os, re, sys, zipfile, html, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
LEX  = os.path.join(ROOT, "my_resources", "lexicons")
MAXPER = 80          # candidates kept per name
RELAX_BELOW = 15     # add relaxed near-misses when strict hits are fewer than this
MAXRELAX    = 25     # and keep at most this many of them

def need(p):
    if not os.path.exists(p):
        sys.exit("Missing: %s\nRun the earlier steps first." % p)
    return p

# ---------------------------------------------------------------- sound classes
# One letter per Turkic consonant class. Vowels are dropped: the match is on the
# consonant skeleton only, because §7 puts vowel recovery near 50%.
CLASS = {}
for ch, cl in [("kq",   "K"), ("gğġγ", "G"), ("hx",  "H"), ("çcč", "C"),
               ("j",    "J"), ("t",    "T"), ("d",   "D"), ("p",   "P"),
               ("b",    "B"), ("vw",   "V"), ("m",   "M"), ("n",   "N"),
               ("ñŋ",   "Q"), ("l",    "L"), ("r",   "R"), ("sşšśṣ","S"),
               ("z",    "Z"), ("y",    "Y")]:
    for c in ch: CLASS[c] = cl

VOWELS = "aeıioöuüâîûäëï"
def starts_vowel(word):
    w = word.lower().strip()
    return bool(w) and w[0] in VOWELS

def skeleton(word):
    """Turkic headword -> consonant-class string. 'ng' is one segment."""
    w = word.lower().strip()
    w = re.sub(r"[̀-ͯ]", "", w)
    out, i = [], 0
    while i < len(w):
        if w.startswith("ng", i):
            out.append("Q"); i += 2; continue
        c = CLASS.get(w[i])
        if c: out.append(c)
        i += 1
    return "".join(out)

# What a Later Han ONSET may stand for, with the majority option first.
# Sourced from data/derived/initial_correspondence.csv (step 15).
ONSET = [
    (("kʰ","k","g","ɣ","x","h"), "KGH",  "K"),   # velars: Chinese g- is usually a source k
    (("ts","tsʰ","tś","tśʰ","dź","dz","ź"), "CJ", "C"),
    (("ṭ","ṭʰ","ḍ","t","tʰ","d"), "TD",  "T"),
    (("p","pʰ","b"),          "PB",   "B"),
    (("m",),                  "M",    "M"),      # step 15: a source b- was written m- 3 times in 838
    (("n","ń","ṇ"),           "N",    "N"),
    (("ŋ",),                  "QN",   "Q"),
    (("l",),                  "LR",   "L"),      # step 15: a source r- was written l- in 12 of 14
    (("ś","ṣ","s"),           "S",    "S"),
    (("j","y"),               "Y",    "Y"),
    (("w","v"),               "VB",   "V"),
    (("ʔ",""),                "",     ""),       # vowel-initial
]
# What a written CODA may stand for. An UNwritten coda may still hide r/l/s/z,
# which the Later Han syllable cannot carry in that position.
CODA = {"k":"KG", "t":"TD", "p":"PB", "m":"M", "n":"N", "ŋ":"QN"}
CODA_IF_ABSENT = "RLSZ"

TONE = "ᴬᴮᶜ"
def strip_tone(s): return "".join(c for c in s if c not in TONE)

def parse_syllable(syl):
    """-> (onset_classes, majority_class, coda_classes, coda_required)"""
    s = strip_tone(syl)
    onset, maj = None, None
    for forms, cls, m in sorted(ONSET, key=lambda t: -max(len(f) for f in t[0])):
        for f in sorted(forms, key=len, reverse=True):
            if f and s.startswith(f):
                onset, maj, s = cls, m, s[len(f):]
                break
        if onset is not None: break
    if onset is None:
        onset, maj = "", ""                      # treat as vowel-initial
        s = s[1:] if s[:1] in "ʔ" else s
    last = s[-1:] if s else ""
    if last in CODA:
        return onset, maj, CODA[last], True
    return onset, maj, CODA_IF_ABSENT, False

def pattern_for(lhan, relax=False):
    """Later Han string -> (regex over skeletons, list of per-syllable majority classes).

    Strict: every written coda must be matched, every syllable must be present.
    Relaxed: all codas optional, every syllable after the first optional, and up to
    two trailing consonants allowed for a suffix. Use it to surface near-misses -
    a shorter root inside a longer name, or a coda the source had lost."""
    syls, majors = [], []
    for syl in lhan.split():
        on, maj, co, req = parse_syllable(syl)
        o = "[%s]" % on if on else ""
        c = "[%s]%s" % (co, "" if (req and not relax) else "?")
        syls.append(o + c)
        majors.append((on, maj))
    if not relax:
        return re.compile("^" + "".join(syls) + "$"), majors
    # Relaxed: codas already optional above; additionally the FINAL syllable may be
    # missing (the name is the headword plus one more element). Nothing else is freed,
    # or the pattern stops discriminating.
    if len(syls) > 2:
        body = "".join(syls[:-1]) + "(?:%s)?" % syls[-1]
    else:
        body = "".join(syls)
    return re.compile("^" + body + "$"), majors

def minority_count(cand_skel, majors, rx):
    """How many onsets of the candidate depart from the majority correspondence."""
    n, i = 0, 0
    for on, maj in majors:
        if not on: continue
        while i < len(cand_skel) and cand_skel[i] not in on: i += 1
        if i < len(cand_skel):
            if maj and cand_skel[i] != maj: n += 1
            i += 1
    return n

# ---------------------------------------------------------------- lexicons
def load_lexicon(path, hk, gk, label):
    rows = []
    if not os.path.exists(path):
        print("  (skipped, not found: %s)" % os.path.basename(path)); return rows
    with io.open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            h = (r.get(hk) or "").strip()
            g = (r.get(gk) or "").strip()
            if h and len(h) < 24:
                rows.append((h, g, label, skeleton(h)))
    print("  %-22s %d headwords" % (label, len(rows)))
    return rows

def epub_words(path):
    """word -> one short context, for verification only."""
    idx = {}
    if not os.path.exists(path): return idx
    try:
        z = zipfile.ZipFile(path)
    except Exception:
        return idx
    for n in z.namelist():
        if not n.lower().endswith((".xhtml", ".html", ".htm")): continue
        try:
            t = z.read(n).decode("utf-8", "ignore")
        except Exception:
            continue
        t = html.unescape(re.sub(r"<[^>]+>", " ", t))
        t = re.sub(r"[ \t\r\n]+", " ", t)
        for m in re.finditer(r"[A-Za-zÇçĞğİıÖöŞşÜüÂâÎîÛûčšžńṇṣśḍṭğ:\-']{3,20}", t):
            w = m.group(0).strip(":-'").lower()
            if w and w not in idx:
                idx[w] = t[max(0, m.start()-60):m.end()+90].strip()
    return idx

# ---------------------------------------------------------------- run
def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    print("Loading lexicons...")
    lexicon  = load_lexicon(os.path.join(DER, "dlt_lexicon.csv"),
                            "headword", "gloss_tr",  "Dīwān (Kāşgarî)")
    lexicon += load_lexicon(os.path.join(DER, "cuman_lexicon.csv"),
                            "headword", "gloss_lat", "Codex Cumanicus")
    if not lexicon:
        sys.exit("No lexicon rows loaded. Run steps 18 and 19 first.")

    print("Indexing Clauson EPUB (this takes a minute)...")
    clauson = epub_words(os.path.join(LEX, "Clauson_1972_EDPT.epub"))
    print("  %d distinct word forms" % len(clauson))

    # bucket the lexicon by skeleton length so the scan is cheap
    by_len = collections.defaultdict(list)
    for row in lexicon: by_len[len(row[3])].append(row)

    src = need(os.path.join(DER, "author_proposals.csv"))
    with io.open(src, encoding="utf-8-sig") as f:
        names = list(csv.DictReader(f))

    out, kept = [], 0
    for r in names:
        ch = r["chinese"]
        if only and only not in ch: continue
        lhan = r["later_han"]
        try:
            rx, majors = pattern_for(lhan)
        except Exception as e:
            print("  ! %s: could not parse %r (%s)" % (ch, lhan, e)); continue
        lo = sum(1 for on, _ in majors if on)
        def scan(rgx, tag):
            got = []
            for L in range(1, lo + len(majors) + 3):
                for h, g, lab, sk in by_len.get(L, ()):
                    if rgx.match(sk):
                        mc = minority_count(sk, majors, rgx)
                        # a vowel-initial word matching a pattern that expects a real
                        # onset is a worse fit than the skeleton alone suggests
                        if majors and majors[0][0] and starts_vowel(h): mc += 1
                        got.append((mc, h, g, lab, sk, tag))
            return got
        hits = scan(rx, "strict")
        if len(hits) < RELAX_BELOW:
            seen = set((t[1], t[3]) for t in hits)
            rx2, _ = pattern_for(lhan, relax=True)
            rel = [t for t in scan(rx2, "relaxed")
                   if (t[1], t[3]) not in seen and len(t[4]) >= 2]
            rel.sort(key=lambda t: (t[0], -len(t[4]), t[1].lower()))
            hits += rel[:MAXRELAX]
        # strict: prefer the tightest fit, so shorter skeletons first.
        hits.sort(key=lambda t: (t[5] != "strict", t[0], len(t[4]), t[1].lower()))
        trunc = len(hits) > MAXPER
        for mc, h, g, lab, sk, tag in hits[:MAXPER]:
            ctx = clauson.get(h.lower(), "")
            out.append({
                "chinese": ch, "pinyin": r["pinyin"], "later_han": lhan,
                "current_proposal": r["proposed_name"], "current_sense": r["proposed_sense"],
                "pattern": rx.pattern, "candidate": h, "candidate_skeleton": sk,
                "lexicon": lab, "gloss": g[:160], "match": tag,
                "minority_steps": mc, "starts_with_vowel": "yes" if starts_vowel(h) else "no",
                "in_clauson": "yes" if ctx else "no",
                "clauson_context": re.sub(r"\s+", " ", ctx)[:200],
            })
        kept += min(len(hits), MAXPER)
        ns = sum(1 for t in hits if t[5] == "strict")
        print("  %-10s %-14s %4d strict %4d relaxed%s" %
              (ch, r["proposed_name"], ns, len(hits) - ns,
               "  (truncated)" if trunc else ""))

    dst = os.path.join(DER, "name_candidates.csv")
    with io.open(dst, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()) if out else ["chinese"])
        w.writeheader(); w.writerows(out)
    print("\nWrote %d rows to data/derived/name_candidates.csv" % kept)
    print("Columns: minority_steps = how many onsets depart from the majority")
    print("         correspondence (0 is best); match = strict or relaxed, and a")
    print("         relaxed hit ignored a written coda or a whole later syllable;")
    print("         in_clauson = the form also occurs")
    print("         in the EDPT text, with a short context for checking.")

if __name__ == "__main__":
    main()
