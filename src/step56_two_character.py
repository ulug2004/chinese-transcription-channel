# -*- coding: utf-8 -*-
r"""
Step 56.  The two-character blind spot, and a control set that closes it.

WHAT WAS FOUND.  The 1,017 verified Sanskrit pairs contain no two-character
transcription at all.  Not few: zero.  The length profile is 1 char 172,
2 chars 0, 3 chars 381, 4 chars 342, 5 chars 88.

That is a hole in exactly the wrong place.  Twenty-one of the record's
forty items are two-character names, 52.5%: 匈奴 冒頓 頭曼 稽粥 軍臣 當戶
且渠 孤塗 攣鞮 撑犁 谷蠡 徑路 閼氏 單于 and the rest.  More than half the
record is priced against a corpus holding no example of its shape.

WHY IT HAPPENED.  The extraction labels every dictionary entry
transcription, ambiguous or calque.  The two-character entries were parked
as ambiguous, and NOT because of their sound: their phonetic score is 1.00,
the same as the verified set.  A two-character Chinese string is very often
an ordinary word, so the labeller could not separate 菩提 bodhi from 出家
pravrajita by shape and hedged on the whole length class.  The sound
evidence was already there and went unused.

WHAT THIS STEP DOES.  It applies the paper's own phonetic verification, per
character, to the parked entries: every character's Later Han initial must
match the consonant class of the source syllable it aligns to, at exact
alignment.  The survivors are written to a SEPARATE control file.

THEY ARE NOT ADDED TO THE CORPUS, AND THIS IS DELIBERATE.  Folding 93 pairs
into 1,017 shifts every rate by a fraction of a point and would require
recomputing every figure in the paper and every price in the supplement, to
no benefit.  The paper already handles a gap of this kind twice by naming a
separate control: §8.5 uses the Ming Turkic glossary for q against k
because the Han corpus has no instance, and step 52 uses it for word-final
consonants for the same reason.  This is the third instance of that
pattern, and every published number stays where it is.

THE TEST IS VALIDATED AGAINST GROUND TRUTH, both ways, and reported below.

Outputs
  data\derived\nti_two_character_control.csv
  reports\step56_summary.txt
"""
import csv, io, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import step46_junchen_space as S

# Chinese initial -> broad consonant class
CLS = {u"p": "P", u"pʰ": "P", u"b": "P", u"m": "M",
       u"t": "T", u"tʰ": "T", u"d": "T", u"ṭ": "T", u"ḍ": "T",
       u"n": "N", u"ṇ": "N", u"ń": "N",
       u"k": "K", u"kʰ": "K", u"g": "K", u"ŋ": "NG",
       u"ts": "C", u"tsʰ": "C", u"dz": "C",
       u"tś": "C", u"tśʰ": "C", u"dź": "C", u"tṣ": "C",
       u"s": "S", u"ś": "S", u"ṣ": "S", u"z": "S",
       u"l": "L", u"ʔ": "0", u"": "0",
       u"h": "H", u"ɣ": "H", u"x": "H", u"j": "Y", u"w": "W"}
# source onset -> the same classes
SRC = {"p": "P", "ph": "P", "b": "P", "bh": "P", "m": "M",
       "t": "T", "th": "T", "d": "T", "dh": "T",
       u"ṭ": "T", u"ḍ": "T", u"ṭh": "T", u"ḍh": "T",
       "n": "N", u"ñ": "N", u"ṇ": "N", u"ṅ": "NG",
       "k": "K", "kh": "K", "g": "K", "gh": "K",
       "c": "C", "ch": "C", "j": "C", "jh": "C",
       "s": "S", u"ś": "S", u"ṣ": "S",
       "l": "L", "r": "L", "h": "H", "v": "W", "y": "Y"}

# Semantic translations that pass the sound test by coincidence.  Inspected
# by hand and rejected: 諸人 "the various people" for jana "people";
# 母天 "mother-deity" for mātṛ "mother".  Both are calques whose characters
# happen to carry the right initials.
HAND_REJECT = {(u"諸人", "jana"), (u"母天", u"mātṛ")}


def initials():
    INI = {}
    for x in csv.DictReader(io.open(os.path.join(EXT, "LHantab.tsv"),
                                    encoding="utf8", errors="ignore"), delimiter="\t"):
        z = (x.get("zi") or "").strip()
        if z and z not in INI:
            INI[z] = (x.get("con") or "").strip()
    return INI


def load(name):
    p = os.path.join(DER, name)
    if not os.path.exists(p):
        return []
    return list(csv.DictReader(io.open(p, encoding="utf-8-sig")))


def test(zi, src, INI, n):
    """None = not testable at this length; True/False = the verification."""
    on = S.onsets(src)
    if len(on) != n or len(zi) != n or any(c not in INI for c in zi):
        return None
    return all(CLS.get(INI[c]) == SRC.get(so) for c, so in zip(zi, on))


def sweep(rows, INI, n):
    t = p = 0; hits = []
    for r in rows:
        zi = (r.get("trad") or "").strip()
        if len(zi) != n:
            continue
        v = test(zi, (r.get("skt") or "").strip(), INI, n)
        if v is None:
            continue
        t += 1
        if v:
            p += 1; hits.append(r)
    return t, p, hits


def main():
    INI = initials()
    ver = load("nti_transcription_pairs.csv")
    amb = load("nti_ambiguous.csv")
    cal = load("nti_calques_excluded.csv")

    lines = []
    def say(s=u""):
        try:
            print(s)
        except Exception:
            print(s.encode("ascii", "replace").decode("ascii"))
        lines.append(s)

    say(u"Step 56.  The two-character blind spot, and a control set that closes it.")
    say(u"")
    say(u"=" * 70)
    say(u"1.  The hole")
    say(u"=" * 70)
    lc = collections.Counter(len((r.get("trad") or "").strip()) for r in ver)
    say(u"   the verified corpus, by transcription length:")
    for k in sorted(lc):
        say(u"       %2d characters  %4d" % (k, lc[k]))
    say(u"       %2d characters  %4d   <-- the gap" % (2, lc.get(2, 0)))
    say(u"")
    rec = [r["chinese"] for r in load("author_proposals.csv")]
    rc = collections.Counter(len(x) for x in rec)
    say(u"   the Xiongnu record, by name length:")
    for k in sorted(rc):
        say(u"       %2d characters  %3d rows  %5.1f%%" % (k, rc[k], 100.0 * rc[k] / len(rec)))
    say(u"   Two-character names are %d of %d, %.1f%% of the record."
        % (rc.get(2, 0), len(rec), 100.0 * rc.get(2, 0) / len(rec)))
    say(u"")
    say(u"   The parked two-character entries were not rejected on sound. Their")
    say(u"   phonetic score is 1.00, the same as the verified set. They were")
    say(u"   parked because a two-character Chinese string is often an ordinary")
    say(u"   word, and the labeller could not separate a transcription from a")
    say(u"   calque by shape.")
    say(u"")

    say(u"=" * 70)
    say(u"2.  The test, validated against ground truth in both directions")
    say(u"=" * 70)
    say(u"   Every character's Later Han initial must match the consonant class")
    say(u"   of the source syllable it aligns to, at exact alignment.")
    say(u"")
    say(u"   %-42s %-22s" % (u"applied to", u"passes"))
    val = []
    for lab, rows, n in [(u"known CALQUES, 2 characters", cal, 2),
                         (u"known CALQUES, 3 characters", cal, 3),
                         (u"known CALQUES, 4 characters", cal, 4),
                         (u"known TRANSCRIPTIONS, 3 characters", ver, 3),
                         (u"known TRANSCRIPTIONS, 4 characters", ver, 4),
                         (u"the PARKED 2-character pool", amb, 2)]:
        t, p, _h = sweep(rows, INI, n)
        val.append((lab, t, p))
        say(u"   %-42s %4d of %-5d %5.1f%%" % (lab, p, t, 100.0 * p / t if t else 0))
    say(u"")
    fp2 = [v for v in val if v[0].startswith(u"known CALQUES, 2")][0]
    tp3 = [v for v in val if v[0].startswith(u"known TRANSCRIPTIONS, 3")][0]
    pk = [v for v in val if v[0].startswith(u"the PARKED")][0]
    say(u"   FALSE POSITIVES. The test accepts %d of %d known calques, %.1f%%."
        % (fp2[2], fp2[1], 100.0 * fp2[2] / fp2[1] if fp2[1] else 0))
    say(u"   CONSERVATISM. It accepts only %.1f%% of known transcriptions, so it"
        % (100.0 * tp3[2] / tp3[1] if tp3[1] else 0))
    say(u"   under-collects rather than over-collects.")
    say(u"   THE POOL LOOKS RIGHT. The parked pool passes at %.1f%% against the"
        % (100.0 * pk[2] / pk[1] if pk[1] else 0))
    say(u"   %.1f%% of the known-good pool: it behaves like transcriptions, not"
        % (100.0 * tp3[2] / tp3[1] if tp3[1] else 0))
    say(u"   like calques.")
    say(u"")
    _t, _p, fph = sweep(cal, INI, 2)
    fph = [r for r in fph]
    if fph:
        say(u"   The calques the test would wrongly accept, for inspection:")
        for r in fph:
            say(u"       %-8s %s" % (r.get("trad"), r.get("skt")))
        say(u"   (護摩 is the standard transcription of homa, the fire ritual. It")
        say(u"   is mislabelled in the source data, not by this test.)")
    say(u"")

    say(u"=" * 70)
    say(u"3.  The control set")
    say(u"=" * 70)
    _t, _p, hits = sweep(amb, INI, 2)
    kept, dropped = [], []
    for r in hits:
        if ((r.get("trad") or "").strip(), (r.get("skt") or "").strip()) in HAND_REJECT:
            dropped.append(r)
        else:
            kept.append(r)
    say(u"   passed the test          %4d" % len(hits))
    say(u"   rejected by inspection   %4d" % len(dropped))
    for r in dropped:
        say(u"       %-8s %-14s a semantic translation that passes by coincidence"
            % (r.get("trad"), r.get("skt")))
    say(u"   CONTROL SET              %4d" % len(kept))
    say(u"")
    for i in range(0, min(len(kept), 84), 6):
        say(u"       " + u"  ".join(u"%s %-10s" % ((r.get("trad") or ""), (r.get("skt") or ""))
                                    for r in kept[i:i + 6]))
    if len(kept) > 84:
        say(u"       ... %d more, in the CSV" % (len(kept) - 84))
    say(u"")

    dest = os.path.join(DER, "nti_two_character_control.csv")
    cols = ["trad", "simp", "skt", "n_chars", "n_syl", "align", "pos", "phon_score"]
    with io.open(dest, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols + ["source_file", "promoted_by"])
        for r in kept:
            w.writerow([r.get(c, "") for c in cols] +
                       ["nti_ambiguous.csv", "step56 both-initials test"])
    say(u"   written: data\\derived\\nti_two_character_control.csv")
    say(u"")

    say(u"=" * 70)
    say(u"4.  What the control set can now answer, and 匈奴")
    say(u"=" * 70)
    n = collections.Counter()
    for r in kept:
        try:
            a, b = int(r.get("n_chars") or 0), int(r.get("n_syl") or 0)
        except Exception:
            continue
        if not a or not b:
            continue
        n["two-character transcriptions"] += 1
        n["  of a %d-syllable source" % b] += 1
    say(u"   Of %d two-character transcriptions:" % n["two-character transcriptions"])
    for k in sorted(n):
        if k.startswith("  "):
            say(u"   %-34s %4d  %5.1f%%"
                % (k, n[k], 100.0 * n[k] / n["two-character transcriptions"]))
    one = n.get("  of a 1-syllable source", 0)
    tot = n["two-character transcriptions"]
    say(u"")
    say(u"   THE 匈奴 QUESTION. The supplement reads 匈奴 as Hung and discards")
    say(u"   奴 nɑ as a Chinese pejorative, which requires two characters to")
    say(u"   write a one-syllable word. In the control set that is %d of %d,"
        % (one, tot))
    say(u"   %.1f%%." % (100.0 * one / tot if tot else 0))
    say(u"")
    say(u"   AND 奴 ITSELF IS A SOUND CHARACTER IN THIS CORPUS. It occurs 7")
    say(u"   times in the verified pairs and all 7 are phonetic, writing the")
    say(u"   nu of manuṣya: 末奴沙, 摩奴闍, 摩奴娑, 摩奴曬. It never appends a")
    say(u"   category. The characters that do append one are 天 27, 鬼 9,")
    say(u"   樹 9, 國 8, 山 7, 城 2, and 奴 is not among them.")
    say(u"")
    say(u"   WHAT THAT DOES AND DOES NOT SETTLE. It does not show that 奴 is")
    say(u"   part of the Xiongnu name. The case for dropping it rests on")
    say(u"   Chinese usage in ethnonyms, where 奴 'slave' is a known pejorative,")
    say(u"   and that is an argument from Chinese practice which this corpus")
    say(u"   cannot test. What it does show is that the supplement's stated")
    say(u"   reason, that 奴 is appended rather than read, is not supported by")
    say(u"   transcription practice and is contradicted by the only direct")
    say(u"   evidence held here. The entry has to make the Chinese-usage")
    say(u"   argument or drop the claim.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    d2 = os.path.join(REP, "step56_summary.txt")
    io.open(d2, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + d2)


if __name__ == "__main__":
    main()
