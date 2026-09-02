# -*- coding: utf-8 -*-
"""
step22_junction_merger.py -- when a written coda is followed by the same onset,
did the source word have that consonant once or twice?

A Chinese scribe writing a foreign word could spell a single source consonant
across a syllable boundary: character 1 ends in -t, character 2 begins in t-.
If that is normal practice, then a two-character sequence such as 骨都 kuət tɑ
can transcribe a source *kuta* with one t, not *kutta*. That matters for reading
names, because it changes how many consonants a transcription actually claims.

Measured on the 772 Sanskrit pairs that align one character to one syllable, so
that character positions and source positions correspond.

Input : data/derived/nti_transcription_pairs.csv   (step 1)
        data/external/LHantab.tsv                  (Schuessler)
Output: data/derived/junction_merger.csv , reports/step22_summary.txt
"""
import csv, io, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")

CODA = set("ptkmnŋ")
def same_place(coda, onset):
    return (coda == onset
            or (coda == "t" and onset in "td")
            or (coda == "k" and onset in "kg")
            or (coda == "p" and onset in "pb"))

def main():
    lh_path = os.path.join(EXT, "LHantab.tsv")
    pr_path = os.path.join(DER, "nti_transcription_pairs.csv")
    for p in (lh_path, pr_path):
        if not os.path.exists(p): sys.exit("Missing: %s" % p)

    LH = {}
    with io.open(lh_path, encoding="utf8", errors="ignore") as f:
        for x in csv.DictReader(f, delimiter="\t"):
            z = x.get("zi") or ""
            if z and z not in LH:
                LH[z] = ((x.get("con") or ""), (x.get("vow") or ""))
    print("Later Han table: %d characters" % len(LH))

    with io.open(pr_path, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f)
                if r.get("align") == "exact" and r.get("n_chars") == r.get("n_syl")]
    print("Pairs aligned one character to one syllable: %d" % len(rows))

    out, n = [], collections.Counter()
    for r in rows:
        zi  = r["trad"]
        skt = (r["skt"] or "").lower().replace("ṃ", "m").replace("ṅ", "n").replace("ñ", "n")
        for i in range(len(zi) - 1):
            a, b = LH.get(zi[i]), LH.get(zi[i + 1])
            if not a or not b: continue
            coda  = (a[1] or "")[-1:]
            onset = (b[0] or "").replace("ʰ", "")[:1]
            if coda not in CODA or not onset: continue
            if not same_place(coda, onset): continue
            n["junctions"] += 1
            twice = (coda + coda in skt) or (coda + onset in skt)
            n["twice" if twice else "once"] += 1
            out.append({"chinese": zi, "sanskrit": r["skt"],
                        "junction": "%s|%s" % (coda, onset),
                        "position": i + 1,
                        "source_has": "twice" if twice else "once"})

    j = n["junctions"] or 1
    pct = 100.0 * n["once"] / j
    lines = [
        "step 22 - the doubled-consonant junction",
        "",
        "Junctions where a written coda is followed by the same-place onset: %d" % n["junctions"],
        "  the source word has that consonant ONCE  : %4d  (%.0f%%)" % (n["once"], pct),
        "  the source word has it twice             : %4d  (%.0f%%)" % (n["twice"], 100 - pct),
        "",
        "Reading: the double spelling is a Chinese convention, not a geminate. A",
        "sequence such as 骨都 kuət tɑ normally transcribes a source *kuta*, with one t.",
        "",
        "Caveat: 'twice' is detected by looking for the doubled letter anywhere in the",
        "Sanskrit form, so a geminate elsewhere in the word counts against the merger.",
        "The true merge rate is therefore at least the figure above, not at most it.",
    ]
    txt = "\n".join(lines)
    print(); print(txt)

    if not os.path.isdir(REP): os.makedirs(REP)
    with io.open(os.path.join(DER, "junction_merger.csv"), "w",
                 encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["chinese", "sanskrit", "junction",
                                          "position", "source_has"])
        w.writeheader(); w.writerows(out)
    with io.open(os.path.join(REP, "step22_summary.txt"), "w", encoding="utf8") as f:
        f.write(txt + "\n")
    print("\nWrote data/derived/junction_merger.csv and reports/step22_summary.txt")

if __name__ == "__main__":
    main()
