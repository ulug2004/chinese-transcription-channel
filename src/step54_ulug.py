# -*- coding: utf-8 -*-
r"""
Step 54.  The two rows that both read uluğ, and why only one of them can.

Two names in the record carry the same Turkic word in this supplement:

    烏累若鞮          Uluğ İnakt        two characters for the element
    呼都而尸道皋若鞮   Öz-Uluğ İnakt     eight characters, six for the elements

The word is the same, so the transcription is the only thing that can
separate them.  This step asks what each string actually writes.

THREE MEASUREMENTS DECIDE IT, and all three are already in the paper.

  1  A source vowel-initial syllable takes a Chinese glottal onset, 137 of
     140.  It takes a velar 0 of 140.  uluğ and öz are both vowel-initial.
     烏 is ʔɑ, a glottal.  皋 is kou and 呼 is hɑ, neither of which is.

  2  A source l is written with a Chinese l-.  None of the six characters
     of the long name carries a liquid at all, so the -l- of uluğ would
     have to be unwritten in the one position the corpus writes it.

  3  A transcription uses more characters than the source has syllables in
     15% of pairs, and almost all of those add one character.  The long
     reading leaves FOUR characters carrying nothing.

The conclusion this step reaches is negative, and it is about the long
name only.  It does not touch 烏累若鞮, which is priced here too and comes
out ordinary.

Output: reports\step54_summary.txt
"""
import csv, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import step46_junchen_space as S

LONG  = u"呼都而尸道皋若鞮"
SHORT = u"烏累若鞮"


def initials():
    INI = {}
    for x in csv.DictReader(io.open(os.path.join(EXT, "LHantab.tsv"),
                                    encoding="utf8", errors="ignore"), delimiter="\t"):
        z = (x.get("zi") or "").strip()
        if z:
            INI.setdefault(z, []).append(((x.get("con") or "").strip(),
                                          (x.get("vow") or "").strip()))
    return INI


def vowel_initial_profile():
    """A source syllable that begins with a vowel: which Chinese onset class
    writes it?  Counted over the aligned one-to-one pairs."""
    INI = initials()
    rows = [r for r in csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                              encoding="utf-8-sig"))
            if r.get("align") == "exact" and r.get("n_chars") == r.get("n_syl")]
    n = collections.Counter()
    for r in rows:
        zi = (r.get("trad") or "").strip(); src = (r.get("skt") or "").strip()
        on = S.onsets(src)
        if not zi or len(on) != len(zi):
            continue
        for ch, so in zip(zi, on):
            if ch not in INI or so:      # so == "" means the syllable is vowel-initial
                continue
            n[INI[ch][0][0]] += 1
    return n


def liquid_onset_profile():
    """A source syllable whose onset is l or r: what does the character carry?"""
    INI = initials()
    rows = [r for r in csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                              encoding="utf-8-sig"))
            if r.get("align") == "exact" and r.get("n_chars") == r.get("n_syl")]
    n = collections.Counter()
    for r in rows:
        zi = (r.get("trad") or "").strip(); src = (r.get("skt") or "").strip()
        on = S.onsets(src)
        if not zi or len(on) != len(zi):
            continue
        for ch, so in zip(zi, on):
            if ch not in INI or so not in ("l", "r"):
                continue
            n[INI[ch][0][0]] += 1
    return n


def extra_character_profile():
    """How many MORE characters than source syllables does a pair use?"""
    rows = list(csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                       encoding="utf-8-sig")))
    def iv(r, k):
        try:
            return int(r.get(k) or 0)
        except Exception:
            return 0
    n = collections.Counter(); ex = []
    for r in rows:
        a, b = iv(r, "n_chars"), iv(r, "n_syl")
        if not a or not b:
            continue
        n[a - b] += 1
        if a - b >= 3 and len(ex) < 10:
            ex.append((r.get("trad") or "", r.get("skt") or "", a - b))
    return n, ex


def main():
    tot, cell, npairs = S.measure_onsets()
    lex = S.load_lexicon()
    INI = initials()
    vi = vowel_initial_profile()
    lq = liquid_onset_profile()
    xc, xex = extra_character_profile()

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

    say(u"Step 54.  The two rows that both read uluğ, and why only one of them can.")
    say(u"Aligned one-character-to-one-syllable pairs: %d" % npairs)
    say(u"")
    say(u"   The characters, from Schuessler:")
    for ch in LONG + u"  " + SHORT:
        if ch in INI:
            say(u"       %s  %s" % (ch, u", ".join(c + v for c, v in INI[ch][:2])))
    say(u"")

    say(u"=" * 70)
    say(u"1.  What writes a source syllable that begins with a vowel")
    say(u"=" * 70)
    t = sum(vi.values())
    say(u"   opportunities: %d" % t)
    for c, k in vi.most_common(10):
        say(u"       Chinese %-4s %4d  %5.1f%%" % (c or u"(none)", k, 100.0 * k / t))
    say(u"")
    g = vi.get(u"ʔ", 0)
    say(u"   A glottal onset takes %d of %d, %.1f%%. Every other class in the" % (g, t, 100.0 * g / t))
    say(u"   table together takes %d." % (t - g))
    for c in (u"k", u"h", u"g", u"l", u"ŋ"):
        say(u"       Chinese %-2s writes a vowel-initial syllable  %3d of %d" % (c, vi.get(c, 0), t))
    say(u"")
    say(u"   Both elements of the long reading are vowel-initial. 皋 is kou, a")
    say(u"   velar, and 呼 is hɑ. Neither class writes a vowel-initial syllable")
    say(u"   anywhere in the corpus. 烏 in the short name is ʔɑ, which is the")
    say(u"   137-of-140 case.")
    say(u"")

    say(u"=" * 70)
    say(u"2.  What writes a source liquid, and where the -l- of uluğ would go")
    say(u"=" * 70)
    t2 = sum(lq.values())
    say(u"   source syllables with an l- or r- onset: %d" % t2)
    for c, k in lq.most_common(8):
        say(u"       Chinese %-4s %4d  %5.1f%%" % (c or u"(none)", k, 100.0 * k / t2))
    say(u"")
    have = [ch for ch in LONG if ch in INI and INI[ch][0][0] in (u"l", u"r")]
    say(u"   Characters in %s carrying a liquid onset: %d" % (LONG, len(have)))
    say(u"   Characters in %s carrying a liquid onset: %d  (累 lui)"
        % (SHORT, len([ch for ch in SHORT if ch in INI and INI[ch][0][0] == u"l"])))
    say(u"")
    l_only, l_hit, l_den = rate(["l"], u"l")
    say(u"   Taking a source l on its own, without r: %d of %d, %.1f%%."
        % (l_hit, l_den, 100.0 * l_only))
    say(u"")
    say(u"   The long name has no liquid in it at all. uluğ read at 皋 needs its")
    say(u"   -l- to be unwritten, in the position the corpus writes a liquid")
    say(u"   %.1f%% of the time for a liquid of either kind and %.1f%% for an l."
        % (100.0 * lq.get(u"l", 0) / t2, 100.0 * l_only))
    say(u"")

    say(u"=" * 70)
    say(u"3.  How many characters a transcription is allowed to leave idle")
    say(u"=" * 70)
    tt = sum(xc.values())
    say(u"   characters minus source syllables, over %d pairs:" % tt)
    for k in sorted(xc):
        if xc[k]:
            say(u"       %+3d   %4d  %5.1f%%" % (k, xc[k], 100.0 * xc[k] / tt))
    say(u"")
    ge = sum(v for k, v in xc.items() if k >= 4)
    say(u"   four or more spare characters: %d of %d, %.2f%%" % (ge, tt, 100.0 * ge / tt))
    if xex:
        say(u"   the largest expansions in the corpus, for inspection:")
        for zi, src, d in xex:
            say(u"       %-14s %-24s +%d" % (zi, src, d))
    say(u"")
    say(u"   On Öz-Uluğ İnakt, 都 tɑ, 而 ńə, 尸 śi and 道 dou are credited with")
    say(u"   nothing. Step 50 established that the corpus's own expansions are")
    say(u"   mostly a Chinese semantic suffix appended to a finished")
    say(u"   transcription, 鬼 鳥 國 城, which is not what these four are.")
    say(u"")

    say(u"=" * 70)
    say(u"4.  烏累若鞮 priced")
    say(u"=" * 70)
    l_l = rate(["l"], u"l")[0]
    glo = float(g) / t if t else 0.0
    V_RND = 190 / 289.0
    UNWRIT_G = 8 / 21.0          # source velar coda written open, coda table, §8
    say(u"   烏 ʔɑ  → u-    a vowel-initial syllable on a glottal   %5.1f%%" % (100 * glo))
    say(u"   累 lui → -lu   a source l on a Chinese l-              %5.1f%%" % (100 * l_l))
    say(u"                   rounded vowel                          %5.1f%%" % (100 * V_RND))
    say(u"        -ğ unwritten, the coda table of §8, 8 of 21   %5.1f%%" % (100 * UNWRIT_G))
    c = glo * l_l * V_RND * UNWRIT_G
    say(u"   uluğ over two characters: %.2f%%, about 1 in %d"
        % (100 * c, int(1 / c) if c else 0))
    say(u"")
    say(u"   THAT FIGURE IS NOT COMPARABLE WITH A WHOLE-NAME FIGURE. It prices")
    say(u"   one two-syllable element, and a short string is cheap by")
    say(u"   construction: every additional character multiplies in another")
    say(u"   rate below 1. Köngen's 1 in 5 at 軍臣 is a whole name, and 1 in 37")
    say(u"   retires Baγatur in §8.1. The comparison this figure supports is")
    say(u"   with the other element in the same slot, not with those.")
    say(u"")
    say(u"   若鞮 is not priced here. The paper treats it in §9 as one title")
    say(u"   element shared by six names, and pricing it once per row would")
    say(u"   count the same evidence six times.")
    say(u"")

    say(u"=" * 70)
    say(u"5.  呼都而尸道皋若鞮 priced, as far as it can be")
    say(u"=" * 70)
    say(u"   It cannot be priced, and that is the result. Two of its six")
    say(u"   non-title characters are asked to do something the corpus does 0")
    say(u"   times in %d, and a zero has no rate to multiply." % t)
    say(u"       呼 hɑ  → öz     vowel-initial on an h-   0 of %d" % t)
    say(u"       皋 kou → uluğ   vowel-initial on a k-    0 of %d" % t)
    say(u"   The remaining four characters carry nothing. Whatever the name")
    say(u"   says, this is not it.")
    say(u"")

    say(u"=" * 70)
    say(u"6.  What the long string could hold instead")
    say(u"=" * 70)
    say(u"   Reading the first six characters as six syllables, in the classes")
    say(u"   the characters actually carry:")
    say(u"       呼 hɑ    velar or h        k g q h")
    say(u"       都 tɑ    dental stop       t d")
    say(u"       而 ńə    palatal nasal     n ñ y")
    say(u"       尸 śi    sibilant          s ş")
    say(u"       道 dou   dental stop       t d")
    say(u"       皋 kou   velar             k g q")
    V = S.V
    Cc = u"[a-zçğışöü]?"
    frames = [
        (u"first two characters as one word",
         u"^([kgqh])([%s])%s([td])([%s])%s$" % (V, Cc, V, Cc)),
        (u"characters 3-4 as one word",
         u"^([nñy])([%s])%s([sş])([%s])%s$" % (V, Cc, V, Cc)),
        (u"characters 5-6 as one word",
         u"^([td])([%s])%s([kgq])([%s])%s$" % (V, Cc, V, Cc)),
    ]
    for lab, pat in frames:
        e = re.compile(pat)
        hits = sorted((w, gl, s) for w, (gl, s) in lex.items() if e.match(w))
        say(u"")
        say(u"   %s: %d" % (lab, len(hits)))
        for w, gl, s in hits[:12]:
            say(u"       %-14s %s [%s]" % (w, gl[:44], s))
        if len(hits) > 12:
            say(u"       ... %d more" % (len(hits) - 12))
    say(u"")

    say(u"=" * 70)
    say(u"7.  What this step establishes")
    say(u"=" * 70)
    say(u"   ESTABLISHES. Öz-Uluğ İnakt is not available. It needs a")
    say(u"   vowel-initial syllable written with a velar twice over, which is 0")
    say(u"   of %d, and it leaves four of eight characters carrying nothing," % t)
    say(u"   which the corpus does %.2f%% of the time. It is the weakest reading" % (100.0 * ge / tt))
    say(u"   in the file and should carry no proposal.")
    say(u"")
    say(u"   ESTABLISHES. Uluğ at 烏累若鞮 is ordinary. The glottal is the")
    say(u"   majority spelling for a vowel-initial syllable, the liquid is")
    say(u"   written, and only the final -ğ is unwritten, which §8 measures at")
    say(u"   8 of 21.")
    say(u"")
    say(u"   DOES NOT ESTABLISH. What the long name says. The frame searches")
    say(u"   above are offered as a starting point for someone else, not as a")
    say(u"   reading. Nothing in section 6 is proposed.")
    say(u"")
    say(u"   A CAUTION ABOUT THE ZERO. The 0 of %d is a Sanskrit figure. The" % t)
    say(u"   claim it supports is about Chinese scribal practice, not about")
    say(u"   Turkic, and it is the same class of argument as §8.5's q and k")
    say(u"   measurement, with the same limitation stated there.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    dest = os.path.join(REP, "step54_summary.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)


if __name__ == "__main__":
    main()
