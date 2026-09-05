# -*- coding: utf-8 -*-
r"""
Step 51.  狐鹿姑, and two objections its own entry gets wrong.

The supplement reads this chanyu's name Kurluga and then argues against
itself:

    "狐 ɣuɑ → kur supplies an -r that Later Han has no coda slot for, and
     鹿 lok → lu discards a coda that was written. Adding an unwritable
     segment and dropping a written one in the same word pulls in
     opposite directions."

Both halves of that are wrong, and the corpus says so.

FIRST.  No Chinese character carries an -r, which is true, but that is not
what "unwritable" should mean here.  A source liquid coda left unwritten
by an open character is the MAJORITY spelling: Table 7 of the paper gives
21 of 37, 57%.  狐 is open.  So kur is the ordinary treatment of a liquid
coda, not an exceptional one.

SECOND.  鹿 lok carries a -k, and the character immediately after it is
姑 kɑ, a velar.  The -k is not discarded: it writes the velar onset of the
next syllable across the junction, which is the device step 22 measured
and which the paper already relies on at 骨都 and elsewhere.  This step
counts how often a written coda does exactly that.

THIRD, and new since the entry was written.  狐 is ɣ-, a velar fricative.
Section 8.5 of the paper measures that a Turkic back q takes an h-class
character 43 times in 66, and kurluga has back vowels throughout.

A caution about a measurement NOT reported here.  An earlier attempt to
count "written codas with nothing in the source to match them" returned
46%, which is wrong: the place-map used covered stops and nasals only, so
every case of a Chinese -t writing a source liquid or sibilant was
miscounted (達 for dhar, 薩 for sar, 末 for mar, 跋 for pas).  That is
Table 7's liquid row, not a new finding.  The figure is not used.

Output: reports\step51_summary.txt
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

PLACE = {"k": "velar", "g": "velar", "kh": "velar", "gh": "velar", u"ṅ": "velar",
         "t": "dental", "d": "dental", "th": "dental", "dh": "dental",
         "n": "dental", u"ṇ": "dental", u"ṭ": "dental", u"ḍ": "dental",
         "p": "labial", "b": "labial", "ph": "labial", "bh": "labial", "m": "labial"}
CP = {"k": "velar", u"ŋ": "velar", "t": "dental", "n": "dental",
      "p": "labial", "m": "labial"}


def junction_rate():
    """Of characters carrying a written coda, how many write the ONSET of the
    following source syllable rather than a coda of their own?"""
    CODA = {}
    for x in csv.DictReader(io.open(os.path.join(EXT, "LHantab.tsv"),
                                    encoding="utf8", errors="ignore"), delimiter="\t"):
        z = (x.get("zi") or "").strip(); v = (x.get("vow") or "")
        if z and z not in CODA:
            CODA[z] = v[-1:] if v[-1:] in "ptkmnŋ" else ""
    rows = [r for r in csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                              encoding="utf-8-sig"))
            if r.get("align") == "exact" and r.get("n_chars") == r.get("n_syl")]

    def parts(s):
        t = S.toks(s); syl = []; cur = []; seen = False
        for k, ch in t:
            if k == "V":
                if seen:
                    syl.append(cur)
                cur = []; seen = True
            else:
                if seen:
                    cur.append(ch)
        if seen:
            syl.append(cur)
        return [(cl[0] if len(cl) >= 2 else None, cl[-1] if cl else None) for cl in syl]

    n = collections.Counter(); ex = []
    for r in rows:
        zi = (r.get("trad") or "").strip(); src = (r.get("skt") or "").strip()
        pr = parts(src)
        if not zi or len(pr) != len(zi):
            continue
        for i, (ch, (coda, nxt)) in enumerate(zip(zi, pr)):
            cc = CODA.get(ch)
            if not cc or i == len(zi) - 1:
                continue                       # word-final codas are a different question
            n["medial characters with a written coda"] += 1
            p = CP.get(cc)
            if coda and PLACE.get(coda) == p:
                n["  writes a coda of its own syllable"] += 1
            elif nxt and PLACE.get(nxt) == p:
                n["  writes the ONSET of the next syllable"] += 1
                if len(ex) < 8:
                    ex.append((zi, src, ch, cc))
            else:
                n["  neither, by a stop-and-nasal test only"] += 1
    return n, ex


def main():
    tot, cell, npairs = S.measure_onsets()
    lex = S.load_lexicon()
    tv = C49.turkic_velars()
    jn, jex = junction_rate()

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

    say(u"Step 51.  狐鹿姑, and two objections its own entry gets wrong.")
    say(u"")
    say(u"=" * 70)
    say(u"1.  Is the -r unwritable, or is it the ordinary spelling?")
    say(u"=" * 70)
    say(u"   Table 7 of the paper: a source liquid coda written with an open")
    say(u"   character, 21 of 37, 57%. It is the majority treatment, and 狐 is")
    say(u"   an open character. The entry calls this 'unwritable'. It is not")
    say(u"   unwritable; it is what a scribe usually did with a liquid.")
    say(u"")

    say(u"=" * 70)
    say(u"2.  Is the -k of 鹿 discarded, or does it write the next onset?")
    say(u"=" * 70)
    t = jn["medial characters with a written coda"]
    for k in ["  writes a coda of its own syllable",
              "  writes the ONSET of the next syllable",
              "  neither, by a stop-and-nasal test only"]:
        say(u"   %-44s %4d  %5.1f%%" % (k, jn[k], 100.0 * jn[k] / t if t else 0))
    say(u"   (of %d medial characters carrying a written coda)" % t)
    say(u"")
    say(u"   Examples of a coda writing the following onset:")
    for zi, src, ch, cc in jex:
        say(u"       %-12s %-22s %s carries -%s" % (zi, src, ch, cc))
    say(u"")
    say(u"   In 狐鹿姑 the character after 鹿 is 姑 kɑ, a velar, and 鹿 carries")
    say(u"   a -k. On the reading kur-lu-ga that -k is the g of ga, written")
    say(u"   across the junction. It is not discarded, and the entry's second")
    say(u"   objection does not hold.")
    say(u"")
    say(u"   The last row above is NOT a measure of discarding. It is inflated")
    say(u"   by a stop-and-nasal place test that miscounts a Chinese -t writing")
    say(u"   a source liquid or sibilant: 達 for dhar, 薩 for sar, 末 for mar.")
    say(u"   Those are Table 7's liquid row. No discard rate is claimed here.")
    say(u"")

    say(u"=" * 70)
    say(u"3.  kurluga priced")
    say(u"=" * 70)
    q_h = q_asp = 0.0
    if tv:
        b = sum(v for (c, i), v in tv.items() if c == u"back q")
        if b:
            q_h = float(tv[(u"back q", u"h-")]) / b
            q_asp = float(tv[(u"back q", u"aspirated k")]) / b
    l_l   = rate(["l"], u"l")[0]
    k_k   = rate(["k"], u"k")[0]
    g_k   = rate(["g", "gh"], u"k")[0]
    V_RND = 190 / 289.0          # source u/o written with a rounded vowel
    V_OPN = 1045 / 1509.0        # source a written with an open vowel
    LIQ   = 21 / 37.0            # source liquid coda left unwritten, Table 7

    say(u"   狐 ɣuɑ  → kur   a back q on an h-class character   %5.1f%%" % (100 * q_h))
    say(u"                    rounded vowel                      %5.1f%%" % (100 * V_RND))
    say(u"                    the -r unwritten, Table 7          %5.1f%%" % (100 * LIQ))
    say(u"   鹿 lok  → lu    a source l on a Chinese l-          %5.1f%%" % (100 * l_l))
    say(u"                    rounded vowel                      %5.1f%%" % (100 * V_RND))
    say(u"                    the -k writes the next onset       (junction, above)")
    say(u"   姑 kɑ   → ga    a source g on a Chinese k-          %5.1f%%" % (100 * g_k))
    say(u"                    open vowel                         %5.1f%%" % (100 * V_OPN))
    say(u"")
    c = q_h * V_RND * LIQ * l_l * V_RND * g_k * V_OPN
    say(u"   Whole name, excluding the junction step: %.3f%%, about 1 in %d"
        % (100 * c, int(1 / c) if c else 0))
    c2 = q_asp * V_RND * LIQ * l_l * V_RND * g_k * V_OPN
    say(u"   On an aspirated reading of the first character instead: 1 in %d"
        % (int(1 / c2) if c2 else 0))
    say(u"")
    say(u"   ONE CONSONANT MOVES IT BY A FACTOR OF FIVE. The figure above")
    say(u"   assumes the last syllable is <ga>, so 姑 writes a source g with a")
    say(u"   Chinese k-, which is %.1f%%. If the word ends in <ka> instead, the" % (100 * g_k))
    say(u"   same character writes a source k, which is %.1f%%:" % (100 * k_k))
    c3 = q_h * V_RND * LIQ * l_l * V_RND * k_k * V_OPN
    say(u"       kurluka   %.3f%%   1 in %d" % (100 * c3, int(1 / c3) if c3 else 0))
    say(u"       kurluga   %.3f%%   1 in %d" % (100 * c, int(1 / c) if c else 0))
    say(u"   Which of the two the Turkic word is has not been settled here.")
    say(u"")
    say(u"   For comparison: 1 in 37 retires Baγatur in §8.1 of the paper.")
    say(u"")

    say(u"=" * 70)
    say(u"4.  What else fits the frame")
    say(u"=" * 70)
    V = S.V
    e = re.compile(u"^([kgqh])([%s])([lr])([lr])([%s])([kgq])([%s])$" % (V, V, V))
    hits = sorted((w, g, s) for w, (g, s) in lex.items() if e.match(w))
    say(u"   Words shaped  velar + V + liquid | liquid + V | velar + V : %d" % len(hits))
    for w, g, s in hits[:12]:
        say(u"       %-14s %s [%s]" % (w, g[:46], s))
    say(u"")
    say(u"   WHAT IS NOT SETTLED")
    say(u"   - kurluga is not itself an attested headword. Check whether it is")
    say(u"     a formation from kur- and on what suffix before proposing it.")
    say(u"   - The q rate is Ming, not Later Han; §8.5 states that limit.")
    say(u"   - The junction step is counted but not priced as a rate here: the")
    say(u"     denominator above excludes it, so the figure is an upper bound.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    dest = os.path.join(REP, "step51_summary.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)


if __name__ == "__main__":
    main()
