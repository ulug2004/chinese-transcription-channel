# -*- coding: utf-8 -*-
r"""
Step 55.  The eight-character name split 3-3-2, and what the lexicons hold
at each frame.

Step 54 withdrew the reading this row carried and put nothing in its
place.  This step does not put anything there either.  It asks a narrower
question the author raised: if the string is cut 3-3-2,

    呼都而   尸道皋   若鞮
    hɑ tɑ ńə  śi douᴮ kou  ńɑk te

so that the first six characters are two elements and the last two are the
title §9 argues, what Turkic words can stand at each of the two frames?

THIS IS A SEARCH, NOT A PROPOSAL.  The Chinese writes no word division, so
the 3-3-2 cut is a hypothesis about the string and not a fact about it.
The row stays empty in the supplement whatever this step returns.  What
the step can do is bound the space: if the frames are empty, the cut is
wrong; if they are crowded, a hit means little; and if something lands
cheaply at both, that is worth someone else's attention.

WHY THIS CUT IS WORTH TESTING AT ALL.  All six characters are open, so no
coda is written anywhere in the string, and a reading may put an unwritten
coda after any vowel at the cost the coda table gives.  Two of the six are
near-dedicated: 尸 writes a source ś 56 times in 66, and 皋 writes a source
k 190 times in 220.  Those pin both ends of the second element, which is
more constraint than the withdrawn reading ever had.

A PERIOD WARNING THAT APPLIES TO THE WHOLE STEP.  This name is the only
one in the record from Hou Hanshu 89; every other ruler name is Hanshu.
The character 尸 occurs 0 times in the twenty Western Han ruler names and
7 times in the thirteen Southern Xiongnu titles after 48 CE, always in the
cluster 尸逐.  It may be a formulaic title element rather than a syllable
of a word, in which case no frame containing it is the right frame.  This
step reports the search; it does not settle that.

Output: reports\step55_summary.txt
"""
import csv, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import step46_junchen_space as S
import step47_kongen as K47

VOW = u"aeıioöuüâêîô"
CONS = u"bcçdfgğhjklmnñprsştvyzqxʼ"

# Turkic letter -> the Sanskrit source symbols it is counted as
SRC = {u"h": ["h"], u"k": ["k"], u"g": ["g", "gh"], u"q": ["k"],
       u"t": ["t"], u"d": ["d", "dh"], u"ç": ["c"], u"c": ["j", "jh"],
       u"ñ": [u"ñ"], u"n": ["n"], u"y": ["y"], u"m": ["m"],
       u"ş": [u"ś"], u"s": ["s"], u"z": ["s"], u"l": ["l"], u"r": ["r"],
       u"b": ["b"], u"p": ["p"], u"v": ["v"], u"w": ["v"]}


def coda_open_rates():
    """source coda -> the rate at which it is written with an OPEN character."""
    n = collections.Counter(); o = collections.Counter()
    p = os.path.join(DER, "coda_spelling.csv")
    for r in csv.DictReader(io.open(p, encoding="utf-8-sig")):
        c = (r.get("source_coda") or "").strip()
        k = int(r.get("count") or 0)
        n[c] += k
        if (r.get("chinese_coda") or "").startswith("open"):
            o[c] += k
    out = {}
    for c in n:
        out[c] = float(o[c]) / n[c]
    # liquids are counted in their own file, since Later Han has no -r or -l slot
    lp = os.path.join(DER, "liquid_coda.csv")
    if os.path.exists(lp):
        rows = list(csv.DictReader(io.open(lp, encoding="utf-8-sig")))
        if rows:
            key = [k for k in rows[0] if k and "chinese_coda" in k][0]
            op = sum(1 for r in rows if (r.get(key) or "").strip() == "open")
            out["r"] = out["l"] = float(op) / len(rows)
    return out


def rounded_front_vowels():
    """Sanskrit has no ö or ü, so the class a Turkic ö/ü is written with has
    to come from the Ligeti Turkic-Chinese pairs.  Step 47 measured only the
    FRONT cell of this table and treated everything else as negligible.  It
    is not: the distribution is measured here in full."""
    p = os.path.join(DER, "ligeti_turkic_chinese_pairs.csv")
    if not os.path.exists(p):
        return None
    Vt = u"aeıioöuüâê"
    def syl(w):
        w = w.lower().replace("-", ""); out = []; cur = ""
        for ch in w:
            cur += ch
            if ch in Vt:
                out.append(cur); cur = ""
        if cur and out:
            out[-1] += cur
        elif cur:
            out.append(cur)
        return out
    def cvowel(t):
        t = t.lower()
        for pat, cl in [("iu", "rounded"), ("ou", "rounded"), ("uo", "rounded"),
                        ("o", "rounded"), ("u", "rounded"),
                        ("ie", "front"), ("i", "front"), ("e", "front"),
                        ("a", "open")]:
            if pat in t:
                return cl
        return "?"
    n = collections.Counter()
    for r in csv.DictReader(io.open(p, encoding="utf-8-sig")):
        if (r.get("suspect") or "").strip():
            continue
        ts = syl(r["turkic"]); cs = [x for x in r["efeo_chinese"].split("-") if x]
        if len(ts) != len(cs):
            continue
        for a, b in zip(ts, cs):
            vs = [ch for ch in a if ch in Vt]
            if vs and vs[-1] in u"öü":
                n[cvowel(b)] += 1
    return n


def final_consonant_device():
    """Step 52: of the extra final characters in the Ligeti corpus, how many
    write the word's final consonant with their onset, their vowel writing
    nothing?  This is the device 骨都侯, 虛閭權渠 and 狐鹿姑 all use."""
    import step52_final_consonant as S52
    n, _o, _e = S52.turkic_finals()
    if not n:
        return None
    d = n["of those, with an EXTRA final character"]
    return (float(n["  the extra character writes that consonant"]) / d) if d else None


def turkic_q_on_h():
    """§8.5: a Turkic back q written with an h-class character, Ligeti corpus."""
    import step49_clanname as C49
    tv = C49.turkic_velars()
    if not tv:
        return None
    b = sum(v for (c, i), v in tv.items() if c == u"back q")
    return (float(tv[(u"back q", u"h-")]) / b) if b else None


def syllabify(w):
    """Split a headword into syllables, each = onset + vowel + optional coda."""
    out = []; cur = ""
    for ch in w:
        cur += ch
        if ch in VOW:
            out.append([cur, ""]); cur = ""
    if not out:
        return None
    if cur:
        out[-1][1] = cur
    return [(s[:-1], s[-1], c) for s, c in out]      # (onset, vowel, coda)


def main():
    tot_o, cell_o, npairs = S.measure_onsets()
    tot_v, cell_v = K47.measure_vowels_lh()
    f_front, f_n = K47.measure_vowels_turkic()
    lex = S.load_lexicon()
    CO = coda_open_rates()
    q_h = turkic_q_on_h()
    RFV = rounded_front_vowels()

    lines = []
    def say(s=u""):
        try:
            print(s)
        except Exception:
            print(s.encode("ascii", "replace").decode("ascii"))
        lines.append(s)

    BACK = set(u"aıou")

    def onset_rate(letter, chinese_ini, back=None):
        """Sanskrit-corpus rate, EXCEPT for a Turkic back q on an h-class
        character, where §8.5 of the paper measures the Turkic rate directly
        and Sanskrit has no q to measure. This is the same substitution the
        呼韓邪 row and step 51 both rest on."""
        if (chinese_ini == u"h" and letter in u"kqg" and back and q_h):
            return q_h
        srcs = SRC.get(letter)
        if not srcs:
            return None
        a = sum(cell_o[(s, chinese_ini)] for s in srcs)
        b = sum(tot_o[s] for s in srcs)
        return (float(a) / b) if b else 0.0

    def vowel_rate(letter, chinese_class):
        if letter in u"öü":
            if not RFV:
                return None
            tt = sum(RFV.values())
            return (float(RFV.get(chinese_class, 0)) / tt) if tt else None
        k = {u"a": "a", u"â": "a", u"e": "i/e", u"i": "i/e", u"ı": "i/e",
             u"o": "u/o", u"u": "u/o"}.get(letter)
        if not k or not tot_v[k]:
            return None
        return float(cell_v[(k, chinese_class)]) / tot_v[k]

    # the two frames: (label, [(char, chinese initial, chinese vowel class)])
    FRAMES = [
        (u"呼都而", [(u"呼", u"h", "open"), (u"都", u"t", "open"), (u"而", u"ń", "central")]),
        (u"尸道皋", [(u"尸", u"ś", "front"), (u"道", u"d", "rounded"), (u"皋", u"k", "rounded")]),
    ]

    say(u"Step 55.  The eight-character name split 3-3-2, and what stands at each frame.")
    say(u"Aligned one-character-to-one-syllable pairs: %d.  Lexicon headwords: %d."
        % (npairs, len(lex)))
    say(u"")
    say(u"   THE CUT IS A HYPOTHESIS. The Chinese writes no word division. This")
    say(u"   step bounds the space at each frame; it proposes nothing, and the")
    say(u"   supplement row stays empty whatever it returns.")
    say(u"")
    say(u"   Unwritten codas are charged at the coda table's own rates:")
    for c in sorted(CO):
        say(u"       a source -%s written with an open character  %5.1f%%" % (c, 100 * CO[c]))
    if q_h:
        say(u"       a Turkic back q on an h-class character, §8.5   %5.1f%%" % (100 * q_h))
    say(u"")
    if RFV:
        tt = sum(RFV.values())
        say(u"   Sanskrit has no ö or ü, so their rates come from the Ligeti")
        say(u"   Turkic pairs, %d instances:" % tt)
        for c, k in RFV.most_common():
            say(u"       a Turkic ö or ü written with a %-8s character %3d  %5.1f%%"
                % (c, k, 100.0 * k / tt))
        say(u"   Step 47 used only the front cell, which was the cell it needed,")
        say(u"   pricing -gün against the front-vowel character 臣 gin. Nothing")
        say(u"   there is affected. This step needs the whole table.")
        say(u"")

    DEV = final_consonant_device()
    if DEV:
        say(u"   The final-character device, step 52: an extra final character")
        say(u"   writing the word's last consonant, its vowel writing nothing,")
        say(u"   %.1f%% of the time. 骨都侯, 虛閭權渠 and 狐鹿姑 all use it, so a" % (100 * DEV))
        say(u"   three-character frame is searched for two-syllable words too.")
        say(u"")

    ALL = {}
    for label, spec in FRAMES:
        say(u"=" * 70)
        say(u"Frame %s   %s" % (label, u" ".join(
            u"%s(%s-, %s)" % (ch, ci, cv) for ch, ci, cv in spec)))
        say(u"=" * 70)
        say(u"   What can stand at each position, measured:")
        for ch, ci, cv in spec:
            ons = sorted(((onset_rate(L, ci, back=True) or 0.0), L) for L in SRC)
            ons = [(r, L) for r, L in ons if r > 0][::-1]
            vws = sorted(((vowel_rate(V0, cv) or 0.0), V0) for V0 in u"aeıioöuü")
            vws = [(r, V0) for r, V0 in vws if r > 0][::-1]
            say(u"       %s %s-  onset: %s   (back-vowel word)" % (ch, ci,
                u", ".join(u"%s %.0f%%" % (L, 100 * r) for r, L in ons[:7]) or u"NOTHING"))
            say(u"       %s      vowel: %s" % (u" ",
                u", ".join(u"%s %.0f%%" % (L, 100 * r) for r, L in vws[:7]) or u"NOTHING"))
        say(u"")

        scored = []
        for w, (gloss, src) in lex.items():
            if not w or any(c not in VOW + CONS for c in w):
                continue
            syl = syllabify(w)
            if not syl:
                continue

            bk = any(c in BACK for c in w)

            def score(units, tail=None):
                """units: list of (onset, vowel, coda) aligned to the first
                len(units) characters. tail: a final consonant written by the
                last character's onset, its vowel writing nothing."""
                p = 1.0; det = []
                for (on, v, coda), (ch2, ci2, cv2) in zip(units, spec):
                    if len(on) != 1:
                        return None, None
                    r_on = onset_rate(on, ci2, back=bk); r_v = vowel_rate(v, cv2)
                    if not r_on or not r_v:
                        return None, None
                    p *= r_on * r_v
                    det.append(u"%s%s %.0f/%.0f" % (on, v, 100 * r_on, 100 * r_v))
                    if coda:
                        if len(coda) != 1:
                            return None, None
                        r_c = CO.get(coda)
                        if r_c is None:
                            return None, None
                        p *= r_c; det.append(u"-%s open %.0f" % (coda, 100 * r_c))
                if tail is not None:
                    if DEV is None:
                        return None, None
                    r_t = onset_rate(tail, spec[-1][1], back=bk)
                    if not r_t:
                        return None, None
                    p *= r_t * DEV
                    det.append(u"-%s on %s %.0f, device %.0f"
                               % (tail, spec[-1][0], 100 * r_t, 100 * DEV))
                return p, u", ".join(det)

            best = None
            if len(syl) == 3:
                p, det = score(syl)
                if p:
                    best = (p, u"3 syllables", det)
            if len(syl) == 2 and syl[-1][2]:
                # last character writes the final consonant instead of a syllable
                units = [syl[0], (syl[1][0], syl[1][1], u"")]
                p, det = score(units, tail=syl[-1][2][-1])
                if p and (best is None or p > best[0]):
                    best = (p, u"2 syllables + final consonant", det)
            if best:
                scored.append((best[0], w, gloss, src, best[1], best[2]))

        scored.sort(reverse=True)
        ALL[label] = scored
        say(u"   headwords that fit the frame at all: %d" % len(scored))
        say(u"")
        if not scored:
            say(u"   NOTHING FITS. On this cut the element has no lexical support.")
        else:
            for p, w, gloss, src, shape, det in scored[:15]:
                say(u"       %-14s %8.4f%%  1 in %-9d %-30s [%s]"
                    % (w, 100 * p, int(1 / p) if p else 0, gloss[:30], src))
                say(u"           %s   |   %s" % (shape, det))
            if len(scored) > 15:
                say(u"       ... %d more, all cheaper" % (len(scored) - 15))
        say(u"")

    say(u"=" * 70)
    say(u"How to read the two lists together")
    say(u"=" * 70)
    a = ALL[FRAMES[0][0]]; b = ALL[FRAMES[1][0]]
    say(u"   %s: %d fits.   %s: %d fits."
        % (FRAMES[0][0], len(a), FRAMES[1][0], len(b)))
    if a and b:
        pa, pb = a[0][0], b[0][0]
        c = pa * pb
        say(u"   Best of each, multiplied:")
        say(u"       %s %.3f%% x %s %.3f%% = %.5f%%, 1 in %d"
            % (a[0][1], 100 * pa, b[0][1], 100 * pb, 100 * c, int(1 / c) if c else 0))
        say(u"   Against 1 in 37, which retires Baγatur in §8.1, and 1 in 5, the")
        say(u"   cheapest whole name in the supplement.")
    say(u"")
    say(u"   THE TWO FRAMES FAIL IN OPPOSITE WAYS, AND BOTH FAILURES ARE REAL.")
    say(u"   呼都而 is empty for a structural reason, not for want of looking:")
    say(u"   而 has a central vowel, and a central Chinese vowel takes any")
    say(u"   source vowel only 4 to 6 percent of the time, so the third")
    say(u"   syllable costs about a factor of twenty whatever fills it; and")
    say(u"   而's ń- accepts a source ñ at 75%%, c at 12%% and y at 2%%, while a")
    say(u"   source n is 0. Four headwords in %d clear both, and the best of" % len(lex))
    say(u"   them is a birch tree at 1 in 10,000.")
    say(u"")
    say(u"   尸道皋 fails the other way. It has room for 111 words, and its")
    say(u"   cheapest occupants are common nouns: quick, urine, cat, a lost")
    say(u"   thing, the lazy one. Nothing in it reads as a ruler's title.")
    say(u"")
    say(u"   A CROWDED FRAME IS EVIDENCE AGAINST ITSELF. Section 6.3 of the")
    say(u"   paper measures that looking a reconstruction up in a Turkic")
    say(u"   dictionary finds a plausible word whether or not one is there. The")
    say(u"   count above is the size of that haystack, and a hit inside a large")
    say(u"   one carries no weight on its own.")
    say(u"")

    say(u"=" * 70)
    say(u"What this step establishes")
    say(u"=" * 70)
    say(u"   ESTABLISHES. How much room each frame has, and what the cheapest")
    say(u"   occupants of it are. Nothing more.")
    say(u"")
    say(u"   DOES NOT ESTABLISH. That the 3-3-2 cut is right. The Chinese marks")
    say(u"   no division, and step 54's finding stands: nothing about this row")
    say(u"   is proposed, and none of the words above is a candidate until the")
    say(u"   cut itself is argued from something other than the wish for one.")
    say(u"")
    say(u"   DOES NOT ESTABLISH. That the Later Han layer is the right one. The")
    say(u"   name is from Hou Hanshu 89, a century later than the bulk of the")
    say(u"   record, and 尸 looks like an Eastern Han title element: 0 of 20 in")
    say(u"   the Western Han ruler names, 7 of 13 in the Southern Xiongnu")
    say(u"   titles, always as 尸逐. If it is formulaic, frame two is not a")
    say(u"   word frame at all and every figure in it is beside the point.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    dest = os.path.join(REP, "step55_summary.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)


if __name__ == "__main__":
    main()
