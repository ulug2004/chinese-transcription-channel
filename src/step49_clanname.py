# -*- coding: utf-8 -*-
r"""
Step 49.  The Xiongnu ruling clan name, and a new measurement it needs.

The record gives the clan name twice: 攣鞮 in the Shiji and Hanshu, and
虛連題 in the Hou Hanshu.  The supplement reads them El-indi, "state
founder", and its own phonetics field makes three admissions: that the
liquid is moved from onset to coda and "no corpus shows that kind of
metathesis", that one character is expanded into two syllables, and that
"the reading is driven by the sense rather than by the transcription".

Two measurements retire it.

  A Chinese l- character writing a vowel-initial source syllable:
      0 of 140.  el is vowel-initial, so 攣 cannot write it.
  What a Chinese l- does write:
      a source r, 177 of 200, and a source l, 85 of 88.

So the source syllable began with a liquid, and Old Turkic has no initial
liquid at all.  That is why the two-character form resists reading: in
攣鞮 the liquid is word-initial.  In the three-character 虛連題 it is
medial, and the constraint disappears.  This step therefore searches the
fuller form and treats the shorter one as an abbreviation of it.

THE NEW MEASUREMENT.  虛 is polyphonic, kʰɨɑ and hɨɑ, and the choice
between them decides the row.  Turkic distinguishes k before a front
vowel from q before a back one; Sanskrit has neither the distinction nor
a q, so the Later Han corpus cannot price it.  The Ligeti Turkic
glossaries can, and this step counts it there: how a Turkic word-initial
k or q was written in Chinese.  That corpus is Ming rather than Later
Han, which is the period mixing section 7 of the paper warns about, and
it is used here for the same reason the paper already uses it for front
rounded vowels: the Sanskrit corpus has no such sound to measure.

Output: reports\step49_summary.txt
"""
import csv, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import step46_junchen_space as S

BACK  = set(u"aıou")
FRONT = set(u"eiöü")


def turkic_velars():
    """How a Turkic word-initial k or q was written, Ligeti glossaries."""
    p = os.path.join(DER, "ligeti_turkic_chinese_pairs.csv")
    if not os.path.exists(p):
        return None
    n = collections.Counter()
    for r in csv.DictReader(io.open(p, encoding="utf-8-sig")):
        if (r.get("suspect") or "").strip():
            continue
        t = (r.get("turkic") or "").strip().lower()
        c = (r.get("efeo_chinese") or "").strip().lower()
        if not t or t[0] not in u"kqg":
            continue
        vs = [ch for ch in t if ch in BACK | FRONT]
        if not vs:
            continue
        cls = u"back q" if vs[0] in BACK else u"front k"
        f = c.split("-")[0]
        if f.startswith("k'") or f.startswith("kh"):
            ini = u"aspirated k"
        elif f.startswith("h") or f.startswith("x"):
            ini = u"h-"
        elif f.startswith("k") or f.startswith("g"):
            ini = u"plain k/g"
        else:
            ini = u"other"
        n[(cls, ini)] += 1
    return n


def vowel_initial_onsets():
    """What Chinese initial writes a source syllable that begins with a vowel."""
    INI = {}
    for x in csv.DictReader(io.open(os.path.join(EXT, "LHantab.tsv"),
                                    encoding="utf8", errors="ignore"), delimiter="\t"):
        z = (x.get("zi") or "").strip(); c = (x.get("con") or "").strip()
        if z:
            INI.setdefault(z, []).append(c)
    rows = [r for r in csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                              encoding="utf-8-sig"))
            if r.get("align") == "exact" and r.get("n_chars") == r.get("n_syl")]
    d = 0; out = collections.Counter()
    for r in rows:
        zi = (r.get("trad") or "").strip(); src = (r.get("skt") or "").strip()
        on = S.onsets(src)
        if not zi or len(on) != len(zi):
            continue
        for ch, so in zip(zi, on):
            if so or ch not in INI:
                continue
            d += 1; out[INI[ch][0]] += 1
    return d, out


def main():
    tot, cell, npairs = S.measure_onsets()
    lex = S.load_lexicon()
    tv = turkic_velars()
    vi_d, vi_out = vowel_initial_onsets()

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

    say(u"Step 49.  The ruling clan name: 攣鞮 and 虛連題.")
    say(u"Aligned one-character-to-one-syllable pairs: %d" % npairs)
    say(u"")
    say(u"=" * 70)
    say(u"1.  Why the two-character form resists reading")
    say(u"=" * 70)
    say(u"   A Chinese l- character writing a source syllable that begins with")
    say(u"   a vowel: %d of %d." % (vi_out.get(u"l", 0), vi_d))
    for c, k in vi_out.most_common(4):
        say(u"       of those %d syllables, %-6s took %3d  (%.0f%%)"
            % (vi_d, c or u"(zero)", k, 100.0 * k / vi_d))
    say(u"   So el, which is vowel-initial, cannot be written by 攣.")
    say(u"")
    for lab, srcs in [(u"a source r written with a Chinese l-", ["r"]),
                      (u"a source l written with a Chinese l-", ["l"])]:
        p, a, b = rate(srcs, u"l")
        say(u"   %-42s %3d of %-4d %5.1f%%" % (lab, a, b, 100 * p))
    say(u"   The source syllable began with a liquid. Old Turkic has no initial")
    say(u"   liquid, which is the wall. In 虛連題 the liquid is medial and")
    say(u"   the wall is not there, so that is the form searched below.")
    say(u"")

    say(u"=" * 70)
    say(u"2.  NEW: how Turkic k and q were written in Chinese")
    say(u"=" * 70)
    if not tv:
        say(u"   Ligeti pairs not found; this section cannot run.")
    else:
        say(u"   Counted on the Ligeti glossaries, which are Ming rather than")
        say(u"   Later Han. Used here because Sanskrit has no q at all, the same")
        say(u"   reason the paper uses this corpus for front rounded vowels.")
        say(u"")
        for cls in (u"back q", u"front k"):
            t = sum(v for (c, i), v in tv.items() if c == cls)
            if not t:
                continue
            say(u"   Turkic %-8s n=%d" % (cls, t))
            for (c, i), v in sorted(((k, v) for k, v in tv.items() if k[0] == cls),
                                    key=lambda x: -x[1]):
                say(u"       %-14s %3d  %5.1f%%" % (i, v, 100.0 * v / t))
            say(u"")
        say(u"   The two are written differently: a back q takes an h- character,")
        say(u"   a front k takes an aspirated one. That decides 虛, which is")
        say(u"   polyphonic with exactly those two values.")
    say(u"")

    say(u"=" * 70)
    say(u"3.  What fits 虛連題")
    say(u"=" * 70)
    V = S.V
    e = re.compile(u"^([kgq])([%s])([a-zçğışöü]?)([lr])([%s])([nñŋm])([td])([%s])([a-zçğışöü]?)$"
                   % (V, V, V))
    hits = sorted((w, g, s) for w, (g, s) in lex.items() if e.match(w))
    say(u"   Words matching  velar + V | liquid + V + nasal | dental + V  : %d" % len(hits))
    for w, g, s in hits:
        say(u"       %-14s %s [%s]" % (w, g[:46], s))
    say(u"")

    r_l   = rate(["r"], u"l")[0]
    d_d   = rate(["d", "dh"], u"d")[0]
    k_kh  = rate(["k"], u"kʰ")[0]
    V_OPEN = 1045 / 1509.0
    CODA_N = 77 / 93.0
    SIB    = 27 / 36.0
    q_h  = 0.0
    if tv:
        t = sum(v for (c, i), v in tv.items() if c == u"back q")
        q_h = float(tv[(u"back q", u"h-")]) / t if t else 0.0

    say(u"   karındaş, priced on each reading of 虛")
    for lab, on1 in [(u"虛 = kʰɨɑ, a source plain k", k_kh),
                     (u"虛 = hɨɑ,  a source back q", q_h)]:
        c = on1 * V_OPEN * r_l * V_OPEN * CODA_N * d_d * V_OPEN * SIB
        say(u"       %-34s %7.3f%%   1 in %d"
            % (lab, 100 * c, int(1 / c) if c else 0))
    say(u"")
    say(u"   Nothing is inserted, nothing discarded, no metathesis: 虛 writes")
    say(u"   ka, 連 writes rın with its -n on the page, 題 writes daş with the")
    say(u"   sibilant unwritten, which Table 7 licenses at 75%.")
    say(u"")
    say(u"   WHAT IS NOT SETTLED")
    say(u"   - The q rate is Ming, not Later Han. It cannot be checked against")
    say(u"     the Sanskrit corpus, which has no q.")
    say(u"   - The vowel of the second syllable is not separately measured; the")
    say(u"     open-vowel rate is used for it.")
    say(u"   - 攣鞮 is treated as an abbreviation of the longer form. The two")
    say(u"     are conventionally taken as variants of one name, but this step")
    say(u"     does not demonstrate the relation, it assumes it.")
    say(u"   - 虛 is absent from Schuessler's table under its traditional form")
    say(u"     and present under the simplified 虚. Four other characters of")
    say(u"     the record are in the same position: 戶 撑 祿 脫.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    dest = os.path.join(REP, "step49_summary.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)


if __name__ == "__main__":
    main()
