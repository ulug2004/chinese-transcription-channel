# -*- coding: utf-8 -*-
"""
step31_liquid_cluster.py -- when a source word has a liquid inside a consonant
cluster, did the scribe write the liquid or drop it?

This is the step the 谷蠡 reading in the supplement turns on. Körklü needs 谷
kok to carry k-ö-r-k, with the -r- unwritten before the written -k. Later Han
has no -r or -l coda, so a source -rC- cannot be written in the coda at all.
The scribe's only way to represent it is to spend an extra character on an l-
syllable. So the question is a counting one: how often was that extra character
spent, and how often was the liquid simply dropped?

Method. For every aligned pair whose source form contains a liquid immediately
followed by a consonant, count the source syllables (vowel nuclei) and the
Chinese characters.
  n_chars == n_syl  ->  no character was spared for the liquid: it is unwritten
  n_chars >  n_syl  ->  an extra character was spent; the script reports whether
                        one of them carries an l- onset, which is the vehicle
                        the corpus uses for a source liquid
Counting this way avoids the circularity of looking only at one-to-one aligned
rows, where an unwritten liquid coda is true by construction.

Input : data/derived/nti_transcription_pairs.csv   (step 1)
        data/external/LHantab.tsv                  (Schuessler)
Output: data/derived/liquid_cluster.csv , reports/step31_summary.txt
"""
import csv, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")

VOWELS = ["ai", "au", "ā", "ī", "ū", "ṝ", "ṛ", "ḷ", "a", "i", "u", "e", "o"]
DIGRAPHS = ["kh", "gh", "ch", "jh", "ṭh", "ḍh", "th", "dh", "ph", "bh"]
LIQUID = set("rl")

def toks(s):
    s = s.lower(); out = []; i = 0
    while i < len(s):
        for v in VOWELS:
            if s.startswith(v, i): out.append(("V", v)); i += len(v); break
        else:
            for d in DIGRAPHS:
                if s.startswith(d, i): out.append(("C", d)); i += len(d); break
            else:
                out.append(("C", s[i])); i += 1
    return out

def nsyl(s):
    return sum(1 for k, _ in toks(s) if k == "V")

def clusters(s):
    """liquid immediately followed by a consonant, e.g. the -rm- of dharma"""
    t = toks(s); out = []
    for i in range(len(t) - 1):
        if t[i][0] == "C" and t[i][1] in LIQUID and t[i+1][0] == "C":
            out.append(t[i][1] + t[i+1][1])
    return out

def main():
    lh = os.path.join(EXT, "LHantab.tsv")
    pr = os.path.join(DER, "nti_transcription_pairs.csv")
    for p in (lh, pr):
        if not os.path.exists(p): sys.exit("Missing: %s" % p)

    ONSET = {}
    with io.open(lh, encoding="utf8", errors="ignore") as f:
        for x in csv.DictReader(f, delimiter="\t"):
            z = (x.get("zi") or "").strip()
            if z and z not in ONSET: ONSET[z] = (x.get("con") or "")

    with io.open(pr, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))   # all 1,017 verified pairs: the
        # align=="exact" subset is 1:1 by construction, so measuring
        # an unwritten consonant inside it would be circular
    print("verified pairs: %d" % len(rows))

    n = collections.Counter(); out = []
    for r in rows:
        zi = (r.get("trad") or "").strip()
        src = (r.get("skt") or "").strip()
        if not zi or not src: continue
        cl = clusters(src)
        if not cl: continue
        ns = nsyl(src); nc = len(zi)
        extra = nc - ns
        has_l = any((ONSET.get(c) or "").startswith("l") for c in zi)
        if extra <= 0:
            verdict = "liquid unwritten"
        elif has_l:
            verdict = "extra character, with an l- onset"
        else:
            verdict = "extra character, no l- onset"
        n[verdict] += 1; n["total"] += 1
        for c in cl: n["cluster:" + c] += 1
        out.append({"chinese": zi, "source": src, "clusters": " ".join(cl),
                    "n_source_syllables": ns, "n_characters": nc,
                    "verdict": verdict})

    tot = n["total"] or 1
    L = []; A = L.append
    A("step 31 - a source liquid inside a consonant cluster")
    A("")
    A("Verified pairs whose source form has a liquid before a consonant: %d" % n["total"])
    for k in ("liquid unwritten", "extra character, with an l- onset",
              "extra character, no l- onset"):
        A("  %-36s %4d  (%.0f%%)" % (k, n[k], 100.0 * n[k] / tot))
    A("")
    A("Reading: Later Han has no liquid coda, so a source -rC- can only be")
    A("represented by spending a further character on an l- syllable. Where the")
    A("character count does not exceed the source syllable count, no character was")
    A("spared and the liquid is unwritten. That is the step the Körklü reading of")
    A("谷蠡 asks for at 谷 kok = körk.")
    A("")
    A("Caveat: 'extra character' is inferred from counts, not from an alignment of")
    A("each character to each syllable, so a pair that compresses elsewhere and")
    A("expands here can be misclassified. The unwritten figure is therefore a floor.")
    A("")
    A("Clusters seen:")
    for k, v in sorted(((k[8:], v) for k, v in n.items() if k.startswith("cluster:")),
                       key=lambda x: -x[1]):
        A("  %-6s %d" % (k, v))
    txt = "\n".join(L)
    print(); print(txt)

    if not os.path.isdir(REP): os.makedirs(REP)
    with io.open(os.path.join(DER, "liquid_cluster.csv"), "w",
                 encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["chinese", "source", "clusters",
                                          "n_source_syllables", "n_characters", "verdict"])
        w.writeheader(); w.writerows(out)
    with io.open(os.path.join(REP, "step31_summary.txt"), "w", encoding="utf8") as f:
        f.write(txt + "\n")
    print("\nWrote data/derived/liquid_cluster.csv and reports/step31_summary.txt")

if __name__ == "__main__":
    main()
