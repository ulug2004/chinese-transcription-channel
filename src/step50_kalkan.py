# -*- coding: utf-8 -*-
r"""
Step 50.  虛閭權渠, and what an unaccounted character costs.

The supplement reads this four-character name as Kalkan, "shield", and its
own phonetics field says: "the first three characters match exactly,
including the written -n coda, at zero minority steps. Only 渠 gɨɑ is left
unaccounted for, and it may carry a separate title element."

Two things are wrong with that as it stands.

First, 渠 is not spare.  The same character writes a full syllable
elsewhere in this record: at 且渠 it carries the ka of the reading proposed
there.  A character with a velar onset and an open vowel is doing work,
not sitting idle.

Second, on the Kalkan reading a second character is nearly idle too.  閭
liɑ is credited with contributing only the -l of kal, its vowel writing
nothing.  So two of the four characters are asked to carry one consonant
between them.

This step measures what that costs, searches the frame at each syllable
count, and re-prices the reading now that section 8.5 of the paper exists:
虛 is polyphonic, kʰɨɑ and hɨɑ, and kalkan has back vowels, so the choice
between those two readings is no longer arbitrary.

Output: reports\step50_summary.txt
"""
import csv, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import step46_junchen_space as S
import step49_clanname as C49

# Chinese characters that append a category to a transcription rather than a sound
SEMANTIC = set(u"鬼鳥國城山王天河江寺神花樹果香子女男人道法經僧佛地水火風海島村林石")


def expansion_profile():
    """Pairs using MORE characters than source syllables, split by what the
    extra character is doing."""
    rows = list(csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                       encoding="utf-8-sig")))
    def iv(r, k):
        try:
            return int(r.get(k) or 0)
        except Exception:
            return 0
    n = collections.Counter()
    sem, pho = [], []
    for r in rows:
        a, b = iv(r, "n_chars"), iv(r, "n_syl")
        if not a or not b:
            continue
        n["total"] += 1
        if a < b:
            n["fewer"] += 1
        elif a > b:
            n["more"] += 1
            zi = (r.get("trad") or "").strip()
            if zi and any(ch in SEMANTIC for ch in zi[-2:]):
                n["more, semantic suffix"] += 1
                if len(sem) < 8:
                    sem.append((zi, (r.get("skt") or "")))
            else:
                n["more, phonetic"] += 1
                if len(pho) < 8:
                    pho.append((zi, (r.get("skt") or "")))
        else:
            n["one to one"] += 1
    return n, sem, pho


def main():
    tot, cell, npairs = S.measure_onsets()
    lex = S.load_lexicon()
    tv = C49.turkic_velars()
    n, sem, pho = expansion_profile()

    lines = []
    def say(s=u""):
        try:
            print(s)
        except Exception:
            print(s.encode("ascii", "replace").decode("ascii"))
        lines.append(s)

    def rate(srcs, ci):
        a = sum(cell[(s, ci)] for s in srcs); b = sum(tot[s] for s in srcs)
        return (float(a) / b if b else 0.0), a, b

    say(u"Step 50.  虛閭權渠, and what an unaccounted character costs.")
    say(u"")
    say(u"=" * 70)
    say(u"1.  How often does a transcription use more characters than syllables?")
    say(u"=" * 70)
    t = n["total"]
    for k, lab in [("one to one", "one character to one syllable"),
                   ("fewer", "fewer characters than syllables (compression)"),
                   ("more", "MORE characters than syllables")]:
        say(u"   %-46s %4d  %5.1f%%" % (lab, n[k], 100.0 * n[k] / t))
    say(u"")
    say(u"   But that last figure is two different things:")
    say(u"      %-42s %4d" % ("a Chinese semantic suffix appended", n["more, semantic suffix"]))
    for zi, src in sem:
        say(u"          %-12s %s" % (zi, src))
    say(u"      %-42s %4d" % ("no obvious suffix: phonetic expansion", n["more, phonetic"]))
    for zi, src in pho:
        say(u"          %-12s %s" % (zi, src))
    say(u"")
    say(u"   The suffix cases are a category label, not a sound: 鬼 demon,")
    say(u"   鳥 bird, 國 country, 城 city. They do not license leaving a")
    say(u"   character unaccounted in a personal name, because the character")
    say(u"   there is not a Chinese classifier.")
    say(u"")
    say(u"   AND 渠 IS NOT SPARE. The same character writes a full syllable at")
    say(u"   且渠 elsewhere in this record. It has a velar onset and an open")
    say(u"   vowel and is doing work there.")
    say(u"")

    say(u"=" * 70)
    say(u"2.  What fits the frame, at each syllable count")
    say(u"=" * 70)
    V = S.V
    Cc = u"[a-zçğışöü]?"
    frames = [
        (u"all four characters, four syllables",
         u"^([kgqh])([%s])%s([lr])([%s])%s([kgq])([%s])([nñŋm])([kgq])([%s])%s$" % (V, Cc, V, Cc, V, V, Cc)),
        (u"three syllables, 渠 left over",
         u"^([kgqh])([%s])%s([lr])([%s])%s([kgq])([%s])([nñŋm])$" % (V, Cc, V, Cc, V)),
        (u"two syllables, 閭 gives only -l and 渠 is left over",
         u"^([kgqh])([%s])([lr])([kgq])([%s])([nñŋm])$" % (V, V)),
    ]
    for lab, pat in frames:
        e = re.compile(pat)
        hits = sorted((w, g, s) for w, (g, s) in lex.items() if e.match(w))
        say(u"")
        say(u"   %s: %d" % (lab, len(hits)))
        for w, g, s in hits[:10]:
            say(u"       %-16s %s [%s]" % (w, g[:44], s))
        if len(hits) > 10:
            say(u"       ... %d more" % (len(hits) - 10))
    say(u"")

    say(u"=" * 70)
    say(u"3.  kalkan priced on each reading of 虛")
    say(u"=" * 70)
    q_h = 0.0
    if tv:
        b = sum(v for (c, i), v in tv.items() if c == u"back q")
        q_h = float(tv[(u"back q", u"h-")]) / b if b else 0.0
    k_kh = rate(["k"], u"kʰ")[0]
    k_k  = rate(["k"], u"k")[0]
    g_g  = rate(["g", "gh"], u"g")[0]
    l_l  = rate(["l"], u"l")[0]
    V_OPEN = 1045 / 1509.0
    CODA_N = 77 / 93.0
    say(u"   kalkan has back vowels, so its velars are q. Section 8.5 measures")
    say(u"   a back q written with an h- character at %.1f%% and with an" % (100 * q_h))
    q_asp = 0.0
    if tv:
        b = sum(v for (c, i), v in tv.items() if c == u"back q")
        q_asp = float(tv[(u"back q", u"aspirated k")]) / b if b else 0.0
    say(u"   aspirated character at %.1f%%." % (100 * q_asp))
    say(u"")
    for lab, on1 in [(u"虛 = hɨɑ,  a source back q", q_h),
                     (u"虛 = kʰɨɑ, a source plain k", k_kh)]:
        c = on1 * V_OPEN * l_l * g_g * V_OPEN * CODA_N
        say(u"       %-32s %7.3f%%   1 in %d"
            % (lab, 100 * c, int(1 / c) if c else 0))
    say(u"")
    say(u"   Those figures price 虛閭權 only. They say nothing about 渠, which")
    say(u"   is the objection, and they assume 閭 may contribute a bare -l.")
    say(u"")
    say(u"   WHAT IS NOT SETTLED")
    say(u"   - No word in the lexicons uses all four characters. If the name is")
    say(u"     one Turkic word, the frame is empty and something is wrong with")
    say(u"     the frame rather than with the search.")
    say(u"   - The three-syllable fits are all -gAn participles, whose suffix")
    say(u"     step 47 established as productive, but none of them reads as a")
    say(u"     ruler's name.")
    say(u"   - kalkan fits only if two of the four characters are nearly idle.")
    say(u"     That is not measured anywhere as a licensed device.")
    say(u"   - 虛 is absent from Schuessler's table under its traditional form")
    say(u"     and present under the simplified 虚, with 戶 撑 祿 脫.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    dest = os.path.join(REP, "step50_summary.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)


if __name__ == "__main__":
    main()
