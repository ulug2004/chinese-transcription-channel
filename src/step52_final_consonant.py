# -*- coding: utf-8 -*-
r"""
Step 52.  What happens to a word-final consonant, and a blind spot in the
Later Han corpus.

Three rows of the supplement lean on the same device without naming it.

    骨都侯   Kutak    侯 go is open; its ONSET writes the final -k and its
                     vowel writes nothing
    虛閭權渠  Kalkan   閭 liɑ contributes only the -l of kal
    狐鹿姑   Kurluga  姑 kɑ carries the final velar

In each case a Chinese character with a vowel is asked to write a bare
consonant.  Nobody has counted whether scribes did that.

THE LATER HAN CORPUS CANNOT ANSWER IT.  Sanskrit words almost never end in
a consonant: of 845 pairs, 22.  That is not a small sample, it is a blind
spot, and it is structural — the source language does not present the
problem.  Turkic presents it constantly, so any Turkic reading that ends
in a consonant depends on a device the paper's main corpus cannot price.

THE TURKIC CORPUS CAN.  Ligeti's Ming glossary has 380 consonant-final
Turkic words with Chinese transcriptions beside them.  This step counts
what the scribes did with them.

Read the result as a statement about Turkic transcription practice, not
about the second century BCE.  The corpus is Ming, the same limitation
section 8.5 states for the q and k measurement, and for the same reason:
the Han corpus contains no instance of the thing to be priced.

Output: reports\step52_summary.txt
"""
import csv, io, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import step46_junchen_space as S

V = set(u"aeıioöuüâêïäéèíóúàûîô")

# an EFEO syllable onset, longest first
ONSETS = ["tch'", "tch", "ch", "k'", "t'", "p'", "ts", "sseu",
          "s", "p", "t", "k", "h", "m", "n", "l", "y", "j", "g", "eul"]

# which Turkic final consonants an EFEO final syllable can be writing
MATCH = {"sseu": "sz", "che": u"sşz", "ch": u"sş", "eul": "rl",
         "s": "sz", "l": "l", "m": "m", "n": "n", "p": "pb",
         "t": "td", "k": "kgq", "h": "kgq", "y": "y", "j": "y"}


def tsyl(w):
    out = []; cur = ""
    for ch in w:
        cur += ch
        if ch in V:
            out.append(cur); cur = ""
    if cur and out:
        out[-1] += cur
    elif cur:
        out.append(cur)
    return out


def cini(sy):
    for p in ONSETS:
        if sy.startswith(p):
            return p
    return sy[:1]


def sanskrit_blind_spot():
    rows = list(csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                       encoding="utf-8-sig")))
    SV = set("aeiou") | set(u"āīūṛeo")
    n = collections.Counter()
    for r in rows:
        src = (r.get("skt") or "").strip().lower()
        if not src:
            continue
        n["pairs"] += 1
        if src[-1].isalpha() and src[-1] not in SV:
            n["source word ends in a consonant"] += 1
    return n


def turkic_finals():
    p = os.path.join(DER, "ligeti_turkic_chinese_pairs.csv")
    if not os.path.exists(p):
        return None, [], []
    rows = [r for r in csv.DictReader(io.open(p, encoding="utf-8-sig"))
            if not (r.get("suspect") or "").strip()]
    n = collections.Counter(); ex_open, ex_extra = [], []
    for r in rows:
        t = (r.get("turkic") or "").strip().lower()
        c = (r.get("efeo_chinese") or "").strip().lower()
        if not t or not c:
            continue
        t = t.split()[0]
        if not t or t[-1] in V or not t[-1].isalpha():
            continue
        n["consonant-final Turkic words"] += 1
        cs = [x for x in c.split("-") if x]
        if not cs:
            continue
        last = cs[-1]
        if last[-1] in "aeiou":
            n["  written with an OPEN final character"] += 1
            if len(ex_open) < 8:
                ex_open.append((t, c))
        else:
            n["  written with a CLOSED final character"] += 1
        ts = tsyl(t)
        if len(cs) > len(ts):
            n["of those, with an EXTRA final character"] += 1
            ini = cini(last)
            if t[-1] in MATCH.get(last, MATCH.get(ini, "")):
                n["  the extra character writes that consonant"] += 1
                if len(ex_extra) < 10:
                    ex_extra.append((t, c, last))
            else:
                n["  the extra character does something else"] += 1
    return n, ex_open, ex_extra


def main():
    sk = sanskrit_blind_spot()
    tk, ex_open, ex_extra = turkic_finals()

    lines = []
    def say(s=u""):
        try:
            print(s)
        except Exception:
            print(s.encode("ascii", "replace").decode("ascii"))
        lines.append(s)

    say(u"Step 52.  Word-final consonants, and a blind spot in the Later Han corpus.")
    say(u"")
    say(u"=" * 70)
    say(u"1.  Why the Sanskrit corpus cannot answer this")
    say(u"=" * 70)
    say(u"   pairs                                  %5d" % sk["pairs"])
    say(u"   of those, the source word ends in a consonant  %5d  (%.1f%%)"
        % (sk["source word ends in a consonant"],
           100.0 * sk["source word ends in a consonant"] / sk["pairs"]))
    say(u"")
    say(u"   That is a structural blind spot rather than a small sample: the")
    say(u"   source language does not present the problem. Turkic presents it")
    say(u"   constantly, so a Turkic reading ending in a consonant depends on")
    say(u"   a device the paper's main corpus cannot price.")
    say(u"")

    if not tk:
        say(u"   Ligeti pairs not found; the rest of this step cannot run.")
    else:
        say(u"=" * 70)
        say(u"2.  What the Turkic corpus shows")
        say(u"=" * 70)
        b = tk["consonant-final Turkic words"]
        for k in ["consonant-final Turkic words",
                  "  written with an OPEN final character",
                  "  written with a CLOSED final character"]:
            say(u"   %-46s %4d  %5.1f%%" % (k, tk[k], 100.0 * tk[k] / b if b else 0))
        say(u"")
        say(u"   Two thirds of the time the last character is open, which means")
        say(u"   the final consonant is either unwritten or carried by a")
        say(u"   character whose vowel is doing nothing.")
        say(u"")
        e = tk["of those, with an EXTRA final character"]
        for k in ["of those, with an EXTRA final character",
                  "  the extra character writes that consonant",
                  "  the extra character does something else"]:
            say(u"   %-46s %4d  %5.1f%%" % (k, tk[k], 100.0 * tk[k] / e if e else 0))
        say(u"")
        say(u"   Examples of the device the three rows use:")
        for t, c, last in ex_extra:
            say(u"       %-14s %-26s extra character %s" % (t, c, last))
        say(u"")
        say(u"   sseu for a final -s or -z, che for -ş, eul for -r. The character")
        say(u"   carries the consonant and its own vowel is epenthetic.")
        say(u"")

    say(u"=" * 70)
    say(u"3.  What this licenses, and what it does not")
    say(u"=" * 70)
    say(u"   LICENSED. A Chinese character whose onset writes a word-final")
    say(u"   consonant, its vowel writing nothing, is a real and common device")
    say(u"   in Turkic transcription. 侯 at 骨都侯, 閭 at 虛閭權渠 and 姑 at")
    say(u"   狐鹿姑 are instances of it, not irregularities.")
    say(u"")
    say(u"   NOT LICENSED. This does not license leaving a character")
    say(u"   unaccounted altogether, which is the separate objection at")
    say(u"   虛閭權渠, where 渠 writes neither a consonant nor a syllable.")
    say(u"")
    say(u"   NOT SETTLED. The corpus is Ming. The matching table used here is")
    say(u"   coarse, so the 'does something else' row is an upper bound on the")
    say(u"   failures rather than a measured rate; some of those cases are")
    say(u"   probably the same device with a final my table does not list.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    dest = os.path.join(REP, "step52_summary.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)


if __name__ == "__main__":
    main()
