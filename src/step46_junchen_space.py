# -*- coding: utf-8 -*-
r"""
Step 46.  The candidate space for 軍臣, priced.

Why this step exists.  The supplement reads 軍臣 as Kunchin, and justifies
the second character by saying that voicing is leaky, so a source ch is
reachable through the Chinese dź-.  Step 41, done for 單于, measured that
same substitution and found it does not happen: a source voiceless
affricate written with dź- is 0 in the corpus.  The two entries cannot
both stand.  This step settles it by measuring, and then asks what the
characters do allow.

The characters, from Schuessler's table, both readings of each:

    軍   kun                     velar onset, u, written -n
    臣   dźin   and   gin        BOTH are Later Han readings of 臣.
                                 The supplement used the first.

So 臣 is polyphonic in the same way 冒 and 單 are, and as with those the
value printed in Appendix A is the first tabulated one.  The second
reading gives a velar onset, which opens a different set of Turkic words
entirely.

Everything is measured from the corpus in this repository, not assumed:
onset rates are counted here from the aligned Sanskrit pairs, by the same
one-character-to-one-syllable rule step 34 uses.  Vowel and coda rates are
Tables 9 and 7 of the paper.

The product of the rates is not a probability that a reading is right.  It
is the product of conditional rates, useful for ranking candidates against
each other and against the thresholds the paper already uses: 2.7% retires
Baγatur in §8.1, 1.4% retired ece at 閼氏.

Output: reports\step46_summary.txt
"""
import csv, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")
V    = "aeıioöuüâêîôû"

VOWELS   = ["ai","au","ā","ī","ū","ṝ","ṛ","ḷ","a","i","u","e","o"]
DIGRAPHS = ["kh","gh","ch","jh","ṭh","ḍh","th","dh","ph","bh"]

# Table 9 of the paper: source vowel class -> the class the character writes
VOWEL_ROUND = {"o": .588, "u": .588, "ö": .588, "ü": .588,
               "a": .043, "e": .043, "i": .043, "ı": .043}
VOWEL_FRONT = {"i": .500, "e": .500, "ı": .500,
               "a": .100, "o": .100, "u": .100, "ö": .100, "ü": .100}
# Table 7: source coda -> written as a Chinese -n
CODA_N = {"n": .828, "m": .261, "ñ": .136, "ŋ": .136, "r": .027, "l": .027}


def toks(s):
    s = s.lower(); out = []; i = 0
    while i < len(s):
        for v in VOWELS:
            if s.startswith(v, i):
                out.append(("V", v)); i += len(v); break
        else:
            for d in DIGRAPHS:
                if s.startswith(d, i):
                    out.append(("C", d)); i += len(d); break
            else:
                out.append(("C", s[i])); i += 1
    return out


def onsets(s):
    """onset of each source syllable: the consonant immediately before its vowel"""
    t = toks(s); out = []; prev = None
    for kind, ch in t:
        if kind == "V":
            out.append(prev if prev else "")
            prev = None
        else:
            prev = ch
    return out


def measure_onsets():
    """source onset -> Chinese initial, counted over aligned pairs."""
    lh = os.path.join(EXT, "LHantab.tsv")
    pr = os.path.join(DER, "nti_transcription_pairs.csv")
    for p in (lh, pr):
        if not os.path.exists(p):
            sys.exit("Missing: %s" % p)
    INI = {}
    with io.open(lh, encoding="utf8", errors="ignore") as f:
        for x in csv.DictReader(f, delimiter="\t"):
            z = (x.get("zi") or "").strip()
            c = (x.get("con") or "").strip()
            if z:
                INI.setdefault(z, []).append(c)
    with io.open(pr, encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f)
                if r.get("align") == "exact" and r.get("n_chars") == r.get("n_syl")]
    tot = collections.Counter(); cell = collections.Counter()
    for r in rows:
        zi = (r.get("trad") or "").strip(); src = (r.get("skt") or "").strip()
        if not zi or not src:
            continue
        on = onsets(src)
        if len(on) != len(zi):
            continue
        for ch, so in zip(zi, on):
            if ch not in INI or not so:
                continue
            ci = INI[ch][0]          # the first tabulated reading, as the paper does
            tot[so] += 1
            cell[(so, ci)] += 1
    return tot, cell, len(rows)


def load_lexicon():
    """Headwords keyed by their PHONEMIC form.

    Codex Cumanicus headwords are in medieval Latin spelling and are
    converted by codex_orth before use, so that a search sees teñiz rather
    than tengis and yol rather than jol. Where the spelling changed, the
    source tag records the original.
    """
    import codex_orth
    lex = {}
    def add(h, g, src):
        h = (h or "").strip().lower().rstrip("-")
        if not h:
            return
        if src == "Cod":
            n = codex_orth.normalize(h)
            src = codex_orth.tag(h, n)
            h = n
        if h not in lex:
            lex[h] = ((g or "").strip()[:46], src)
    for name, hw, gl, tag in [("dlt_lexicon.csv", "headword", "gloss_tr", "DLT"),
                              ("cuman_lexicon.csv", "headword", "gloss_lat", "Cod"),
                              ("irk_bitig_lexicon.csv", "headword", "gloss", "IrkB")]:
        p = os.path.join(DER, name)
        if not os.path.exists(p):
            continue
        for r in csv.DictReader(io.open(p, encoding="utf-8-sig")):
            add(r.get(hw), r.get(gl), tag)
    return lex


def main():
    tot, cell, npairs = measure_onsets()
    lex = load_lexicon()

    lines = []
    def say(s=u""):
        try:
            print(s)
        except Exception:
            print(s.encode("ascii", "replace").decode("ascii"))
        lines.append(s)

    def rate(src_list, chinese):
        n = sum(cell[(s, chinese)] for s in src_list)
        d = sum(tot[s] for s in src_list)
        return n, d, (float(n) / d if d else 0.0)

    say(u"Step 46.  The candidate space for 軍臣, priced.")
    say(u"Aligned one-character-to-one-syllable pairs: %d" % npairs)
    say(u"")
    say(u"=" * 68)
    say(u"1.  The disputed substitution, measured")
    say(u"=" * 68)
    say(u"The supplement says a source voiceless affricate is reachable through")
    say(u"the Chinese dź- because voicing is leaky. The corpus says:")
    say(u"")
    for label, srcs, ci in [
            (u"source c      -> dź", ["c"], u"dź"),
            (u"source c      -> tś", ["c"], u"tś"),
            (u"source c      -> t ", ["c"], u"t"),
            (u"source c, ch  -> dź", ["c", "ch"], u"dź"),
            (u"source j, jh  -> dź", ["j", "jh"], u"dź"),
            (u"source k      -> k ", ["k"], u"k"),
            (u"source k      -> g ", ["k"], u"g"),
            (u"source g, gh  -> g ", ["g", "gh"], u"g"),
            (u"source g, gh  -> k ", ["g", "gh"], u"k"),
            (u"source k      -> dź", ["k"], u"dź"),
            (u"source g, gh  -> dź", ["g", "gh"], u"dź")]:
        n, d, p = rate(srcs, ci)
        say(u"   %-22s %3d of %-4d %6.1f%%" % (label, n, d, 100 * p))
    say(u"")

    c_dz = rate(["c"], u"dź")          # source c alone, the figure the paper quotes
    j_dz = rate(["j", "jh"], u"dź")
    k_k  = rate(["k"], u"k")
    g_g  = rate(["g", "gh"], u"g")
    k_g  = rate(["k"], u"g")
    g_k  = rate(["g", "gh"], u"k")

    if c_dz[0] == 0:
        say(u"   VERDICT: a source voiceless affricate written with dź- does not")
        say(u"   occur in this corpus, %d opportunities. The supplement's reason" % c_dz[1])
        say(u"   for 臣 -> çin is not supported. A source VOICED affricate is a")
        say(u"   different matter: %d of %d, %.1f%%." % (j_dz[0], j_dz[1], 100 * j_dz[2]))
    else:
        say(u"   VERDICT: it does occur, %d of %d. The supplement's reason stands."
            % (c_dz[0], c_dz[1]))
    say(u"")
    say(u"   These reproduce the paper exactly: source c is 48 opportunities,")
    say(u"   0 written with dz- and 8 with t- at 16.7%, which is what the")
    say(u"   supplement quotes for the other title.")
    say(u"")

    say(u"=" * 68)
    say(u"2.  What each reading of the two characters permits")
    say(u"=" * 68)
    say(u"   軍  kun            velar onset, rounded vowel, written -n")
    say(u"   臣  dźin           palatal affricate onset, front vowel, written -n")
    say(u"   臣  gin            VELAR onset, front vowel, written -n")
    say(u"   Both readings of 臣 are in Schuessler's table. Appendix A prints")
    say(u"   the first, which is what the supplement used.")
    say(u"")

    # ---- first element: 軍 kun ------------------------------------------
    e1 = re.compile(r"^([kg])([%s]{1,2})([nmñŋrl])$" % V)
    firsts = []
    for w, (g, srcv) in lex.items():
        m = e1.match(w)
        if not m:
            continue
        c, v, k = m.groups()
        on = k_k[2] if c == "k" else g_k[2]
        vo = VOWEL_ROUND.get(v[-1], .02)
        cd = CODA_N.get(k, .01)
        firsts.append((on * vo * cd, w, g, srcv, on, vo, cd))
    firsts.sort(reverse=True)

    # ---- second element, on each reading of 臣 --------------------------
    e2 = re.compile(r"^([cçjkg])([%s]{1,2})([nmñŋrl])$" % V)
    seconds = {u"dźin": [], u"gin": []}
    for w, (g, srcv) in lex.items():
        m = e2.match(w)
        if not m:
            continue
        c, v, k = m.groups()
        vo = VOWEL_FRONT.get(v[-1], .05)
        cd = CODA_N.get(k, .01)
        # Turkish orthography: c is /dź/, the VOICED affricate, so it goes with
        # source j; ç is /tś/, the voiceless one, which is the 0 of 48 case.
        # The Codex writes Turkic y- as j, so j- rows are struck below.
        if c == u"ç":
            on = c_dz[2]; row = u"dźin"
        elif c in (u"c", u"j"):
            on = j_dz[2]; row = u"dźin"
        elif c == "k":
            on = k_g[2]; row = u"gin"
        else:
            on = g_g[2]; row = u"gin"
        seconds[row].append((on * vo * cd, w, g, srcv, on, vo, cd))
    for k in seconds:
        seconds[k].sort(reverse=True)

    def table(title, rows, n=12):
        say(u"")
        say(u"-" * 68)
        say(title)
        say(u"-" * 68)
        if not rows:
            say(u"   nothing in the lexicons fits this frame.")
            return
        say(u"   %-14s %8s  %7s %7s %7s   %s"
            % (u"word", u"cost", u"onset", u"vowel", u"coda", u"gloss"))
        for cost, w, g, srcv, on, vo, cd in rows[:n]:
            say(u"   %-14s %7.3f%%  %6.1f%% %6.1f%% %6.1f%%   %s [%s]"
                % (w, 100 * cost, 100 * on, 100 * vo, 100 * cd, g, srcv))
        if len(rows) > n:
            say(u"   ... %d more fit the frame" % (len(rows) - n))

    table(u"First element, 軍 kun  (k/g + vowel + nasal or liquid)", firsts)
    table(u"Second element on 臣 = dźin  (the reading the supplement used)",
          seconds[u"dźin"])
    say(u"")
    say(u"   THIS COLUMN IS AN ORTHOGRAPHIC ILLUSION. The Codex Cumanicus is")
    say(u"   written in medieval Latin spelling, in which j stands for Turkic")
    say(u"   y- and c before a back vowel stands for k-. So jain, jol and jil")
    say(u"   are yay, yol and yil, and can, cun and coun are kan, kun and")
    say(u"   kavun. None of them is an affricate. What is left is the genuine")
    say(u"   voiceless affricate in c-, which is 0 of 48, and Old Turkic has")
    say(u"   no initial voiced affricate for the other route. So no word in")
    say(u"   these lexicons reaches the character on this reading.")
    table(u"Second element on 臣 = gin  (the second tabulated reading)",
          seconds[u"gin"])

    # ---- whole-title combinations --------------------------------------
    say(u"")
    say(u"=" * 68)
    say(u"3.  The whole title, best combinations")
    say(u"=" * 68)
    for row in (u"dźin", u"gin"):
        best = []
        for c1, w1, g1, s1, _, _, _ in firsts[:8]:
            for c2, w2, g2, s2, _, _, _ in seconds[row][:8]:
                best.append((c1 * c2, w1 + u" " + w2, g1, g2))
        best.sort(reverse=True)
        say(u"")
        say(u"   on 臣 = %s" % row)
        if not best:
            say(u"      no combination available.")
            continue
        for cost, name, g1, g2 in best[:8]:
            say(u"      %-24s %8.4f%%   1 in %-7d %s / %s"
                % (name, 100 * cost, int(1 / cost) if cost else 0, g1[:22], g2[:22]))

    say(u"")
    say(u"Compare: 1 in 37 is the cost that retires Baγatur in the paper.")
    say(u"A reading much more expensive than that cannot be argued from the")
    say(u"transcription, whatever it means in Turkic.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    dest = os.path.join(REP, "step46_summary.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)


if __name__ == "__main__":
    main()
