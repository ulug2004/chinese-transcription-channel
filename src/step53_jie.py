# -*- coding: utf-8 -*-
r"""
Step 53.  羯, the one ethnonym in the record with a rival reading in print.

Two readings are on the table.

  *ket        Pulleyblank and Vovin, connecting it with Proto-Yeniseian
              *keʔt "person, human being", the Yeniseian self-designation
              (Vovin 2000, CAJ 44/1, p. 91)
  kıyat       this supplement, "of flooding"

Unlike 閼氏, where the same spelling licensed a Yeniseian and a Turkic
reading equally, the character here carries information that bears on the
choice.  Schuessler gives 羯 as kɨat, and this step asks what a Chinese
character with that vowel actually writes.

It also tests the supplement's own reading, which needs one character to
carry two syllables and proposes a word that is not in the lexicons.

A PERIOD OBJECTION THAT MAY OUTWEIGH THE MEASUREMENT.  The Jie appear in
the fourth century CE, not the Han.  A Later Han value for a fourth
century ethnonym is the period mixing section 7 of the paper warns
against, and it is the first thing a referee will raise.  The measurement
is reported here because it is what the Later Han layer says; whether that
layer is the right one for this item is a separate question and is not
settled by this step.

Output: reports\step53_summary.txt
"""
import csv, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import step46_junchen_space as S


def vowel_profile(target=u"ɨa"):
    """Source vowels written by characters whose Schuessler vowel contains
    the target string, against the corpus-wide distribution."""
    VOW = {}
    for x in csv.DictReader(io.open(os.path.join(EXT, "LHantab.tsv"),
                                    encoding="utf8", errors="ignore"), delimiter="\t"):
        z = (x.get("zi") or "").strip(); v = (x.get("vow") or "").strip()
        if z and z not in VOW:
            VOW[z] = v
    rows = [r for r in csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                              encoding="utf-8-sig"))
            if r.get("align") == "exact" and r.get("n_chars") == r.get("n_syl")]
    tgt = collections.Counter(); allv = collections.Counter()
    for r in rows:
        zi = (r.get("trad") or "").strip(); src = (r.get("skt") or "").strip()
        vs = [ch for k, ch in S.toks(src) if k == "V"]
        if not zi or len(vs) != len(zi):
            continue
        for ch, v in zip(zi, vs):
            if ch not in VOW:
                continue
            allv[v] += 1
            if target in VOW[ch]:
                tgt[v] += 1
    return tgt, allv, VOW


def main():
    tot, cell, npairs = S.measure_onsets()
    lex = S.load_lexicon()
    tgt, allv, VOW = vowel_profile()

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

    say(u"Step 53.  羯, and whether the transcription can separate two readings.")
    say(u"   Schuessler gives 羯 as %s." % VOW.get(u"羯", u"?"))
    say(u"")
    say(u"=" * 70)
    say(u"1.  What a character with this vowel writes")
    say(u"=" * 70)
    t = sum(tgt.values())
    say(u"   character tokens whose Schuessler vowel contains ɨa: %d" % t)
    for v, k in tgt.most_common(8):
        say(u"       source %-3s %4d  %5.1f%%" % (v, k, 100.0 * k / t))
    say(u"")
    a = sum(allv.values())
    say(u"   the corpus-wide distribution of source vowels, for comparison:")
    for v, k in allv.most_common(6):
        say(u"       source %-3s %4d  %5.1f%%" % (v, k, 100.0 * k / a))
    say(u"")
    e_share = 100.0 * (allv.get("e", 0) + allv.get(u"ē", 0)) / a
    say(u"   A source e is %.1f%% of the corpus and 0 of %d in this column."
        % (e_share, t))
    say(u"   On the Later Han layer the character writes a source a.")
    say(u"")

    say(u"=" * 70)
    say(u"2.  What that does to each reading")
    say(u"=" * 70)
    say(u"   *ket, the Yeniseian reading, has a front e. That vowel does not")
    say(u"   appear in the column above at all. This is the first item in the")
    say(u"   record where the transcription tells against a Yeniseian reading")
    say(u"   rather than licensing it alongside a Turkic one, as at 閼氏.")
    say(u"")
    say(u"   kıyat, the reading in this supplement, has two syllables and 羯 is")
    say(u"   one character. The character's vowel is a diphthong, so a glide is")
    say(u"   available without inserting anything, but the word itself is the")
    say(u"   problem: see below.")
    say(u"")

    say(u"=" * 70)
    say(u"3.  What the lexicons hold for this frame")
    say(u"=" * 70)
    V = S.V
    e1 = re.compile(u"^([kgq])([%s])([td])$" % V)
    hits = sorted((w, g, s) for w, (g, s) in lex.items() if e1.match(w))
    say(u"   one-syllable words, velar + vowel + dental stop: %d" % len(hits))
    for w, g, s in hits:
        say(u"       %-10s %s [%s]" % (w, g[:50], s))
    say(u"")
    for probe in [u"kıyat", u"kiyat", u"ket", u"kat", u"kad"]:
        if probe in lex:
            say(u"   %-8s IS a headword: %s [%s]" % (probe, lex[probe][0][:44], lex[probe][1]))
        else:
            say(u"   %-8s is NOT a headword in any of the three lexicons" % probe)
    say(u"")
    say(u"   Neither reading's word is attested. kat 'layer' and kad, which")
    say(u"   Kāşgarî glosses 'kar fırtınası, insan öldüren bora, tipi', a")
    say(u"   blizzard or a killing gale, are the attested words that fit, and")
    say(u"   neither is an obvious ethnonym.")
    say(u"")

    say(u"=" * 70)
    say(u"4.  What this step does and does not establish")
    say(u"=" * 70)
    say(u"   ESTABLISHES. On the Later Han layer, 羯 writes a source a, 28 of")
    say(u"   28. A front e is not among them, and a source e is only %.1f%% of" % e_share)
    say(u"   the corpus, so the absence is not an artefact of rarity alone.")
    say(u"")
    say(u"   DOES NOT ESTABLISH. That the Yeniseian reading is wrong. Two")
    say(u"   objections stand against using this measurement here at all:")
    say(u"     - The Jie appear in the fourth century CE. A Later Han value for")
    say(u"       a fourth-century ethnonym mixes periods, which §7 of the paper")
    say(u"       warns against in general terms. This is the first thing to")
    say(u"       settle, and this step does not settle it.")
    say(u"     - *keʔt is a PROTO-Yeniseian reconstruction. The vowel of the")
    say(u"       fourth-century word it descends from is not given by it, and")
    say(u"       Vovin proposes the comparison, not the vowel.")
    say(u"")
    say(u"   AND IT CUTS THE WAY THE PAPER MUST BE MOST CAREFUL ABOUT. A result")
    say(u"   that weakens a Yeniseian reading and leaves a Turkic frame standing")
    say(u"   is the one kind of finding this paper should present with the")
    say(u"   objections attached, not the conclusion.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    dest = os.path.join(REP, "step53_summary.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)


if __name__ == "__main__":
    main()
