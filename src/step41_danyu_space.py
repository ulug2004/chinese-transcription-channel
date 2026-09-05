# -*- coding: utf-8 -*-
"""
Step 41.  The candidate space for 單于, priced.

單 is dźan or tɑn; 于 is wɑ.  This enumerates every reading the two
characters permit, restricted to words actually attested in the medieval
lexicons, and prices each step against the corpus.  Rates are forward
rates, the form the paper uses: given that the source had X, how often did
a scribe write it this way.

    onset of 單    source -> Chinese dź- or t-
    vowel of 單    source vowel class -> a Chinese open vowel   (Table 9)
    coda of 單     source coda -> a written -n                  (Table 7)
    onset of 于    source -> Chinese w-
    vowel of 于    as above
    coda of 于     source coda -> written with an open character (Table 7)

The product is not a probability of the reading being right.  It is the
product of six conditional rates, and it is useful only for ranking
candidates against each other and against the thresholds the paper already
uses elsewhere: 2.7% retires Baγatur in §8.1, and 1.4% was the cost that
retired ece at 閼氏.

Output: reports\\step41_summary.txt
"""
import csv, io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
OUT  = os.path.join(ROOT, "reports")
V    = "aeıioöuüâêîôû"

# ---- measured rates -----------------------------------------------------
ONSET1_DZ = {"c": .387, "ç": .387, "j": .387}          # source affricate -> dź-, 12 of 31
ONSET1_T  = {"t": .302, "d": .302, "c": .167, "ç": .167}  # -> t-, 55 of 182 / 8 of 48
VOWEL_OPEN = {"a": .791, "e": .059, "i": .059, "ı": .059,
              "o": .272, "u": .272, "ö": .272, "ü": .272}   # Table 9
CODA1 = {"n": .828, "m": .261, "ñ": .136, "ŋ": .136, "r": .027}  # -> written -n
CODA2 = {"": 1.0, "r": .568, "l": .568, "ş": .750, "s": .750, "z": .750,
         "k": .381, "g": .381, "ğ": .381, "t": .283, "d": .283,
         "p": .200, "b": .200, "v": .200, "m": .174, "n": .129,
         "ñ": .091, "ŋ": .091, "y": .350}                 # unwritten; -y unmeasured, placeholder
ONSET2 = {"b": .018, "y": .010}      # source -> Chinese w-;  b 1 of 55, y 1 of 98

def load():
    lex = {}
    def add(h, g, src):
        h = (h or "").strip().lower().rstrip("-")
        if h and h not in lex:
            lex[h] = (g or "").strip()[:44] + "  [" + src + "]"
    for r in csv.DictReader(io.open(os.path.join(DER, "dlt_lexicon.csv"),
                                    encoding="utf-8-sig")):
        add(r["headword"], r["gloss_tr"], "DLT")
    for r in csv.DictReader(io.open(os.path.join(DER, "cuman_lexicon.csv"),
                                    encoding="utf-8-sig")):
        add(r["headword"], r["gloss_lat"], "Cod")
    p = os.path.join(DER, "irk_bitig_lexicon.csv")
    if os.path.exists(p):
        for r in csv.DictReader(io.open(p, encoding="utf-8-sig")):
            add(r["headword"], r["gloss"], "IrkB")
    return lex

def main():
    lex = load()
    e1 = re.compile(r"^([cçjtd])([%s]{1,2})([nñŋmr])$" % V)
    e2 = re.compile(r"^([by])([%s]{1,2})([a-zçğışöü]?)$" % V)
    first, second = [], []
    for w, g in lex.items():
        m = e1.match(w)
        if m:
            c, v, k = m.groups()
            for row, tab in (("dź", ONSET1_DZ), ("t", ONSET1_T)):
                if c in tab:
                    cost = tab[c] * VOWEL_OPEN.get(v[-1], .05) * CODA1.get(k, .01)
                    first.append((cost, w, g, row, tab[c], VOWEL_OPEN.get(v[-1], .05), CODA1.get(k, .01)))
        m = e2.match(w)
        if m:
            c, v, k = m.groups()
            if c not in ONSET2 or (k and k not in CODA2):
                continue
            cost = ONSET2[c] * VOWEL_OPEN.get(v[-1], .05) * CODA2.get(k, .05)
            second.append((cost, w, g, ONSET2[c], VOWEL_OPEN.get(v[-1], .05), CODA2.get(k, .05)))
    first.sort(reverse=True); second.sort(reverse=True)

    lines = []
    def say(s=""):
        print(s); lines.append(s)
    say("Step 41.  The candidate space for 單于, priced.")
    say("Rates are forward: given the source had X, how often a scribe wrote it so.")
    say("Compare against the thresholds the paper already uses: 2.7% retires")
    say("Baγatur in §8.1, 1.4% retired ece at 閼氏.")
    say("")
    say("Cheapest first. COST is 'one in N': how many times the corpus would")
    say("have to offer this frame before a scribe wrote it this way once.")
    say("Small N is cheap. The paper retires Baγatur at 1 in 37.")
    say("")
    say("FIRST ELEMENT  (單, written dźan or tɑn, with the -n on the page)")
    say("  %-10s %-5s %6s %6s %6s %10s  %s" % ("Turkish","單","onset","vowel","coda","COST","gloss"))
    for cost, w, g, row, a, b, c in first[:16]:
        say("  %-10s %-5s %5.0f%% %5.0f%% %5.0f%%  1 in %-4.0f  %s"
            % (w, row, a*100, b*100, c*100, 1.0/cost, g))
    say("")
    say("SECOND ELEMENT  (于, written wɑ, open, so any coda is unwritten)")
    say("  %-10s %6s %6s %6s %10s  %s" % ("Turkish","onset","vowel","coda","COST","gloss"))
    for cost, w, g, a, b, c in second[:16]:
        say("  %-10s %5.1f%% %5.0f%% %5.0f%%  1 in %-4.0f  %s"
            % (w, a*100, b*100, c*100, 1.0/cost, g))
    say("")
    say("WHOLE TITLE, best combinations")
    say("  %-22s %11s  %s" % ("Turkish", "COST", "the two glosses"))
    combos = []
    for c1, w1, g1, row, *_ in first[:12]:
        for c2, w2, g2, *_ in second[:12]:
            combos.append((c1 * c2, "%s %s" % (w1, w2), row, g1, g2))
    combos.sort(reverse=True)
    for cost, name, row, g1, g2 in combos[:20]:
        say("  %-22s 1 in %-6.0f  %s | %s" % (name.title(), 1.0/cost, g1[:26], g2[:26]))
    say("")
    say("Every one of these is below the 2.7%% threshold, and the reason is")
    say("the same in all of them: the onset of 于. A source b- written with a")
    say("Chinese w- character is 1 of 55, and no choice of word changes it.")

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    io.open(os.path.join(OUT, "step41_summary.txt"), "w",
            encoding="utf-8").write("\n".join(lines) + "\n")
    print("")
    print("written: " + os.path.join(OUT, "step41_summary.txt"))

if __name__ == "__main__":
    main()
