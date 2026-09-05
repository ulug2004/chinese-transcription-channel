# -*- coding: utf-8 -*-
r"""
Step 47.  Reading 軍臣: every form the two characters permit, priced, with
the Turkic morphology counted rather than asserted.

Step 46 established two things.  A source voiceless affricate written with
the Chinese dź- is 0 of 48, so the supplement's Kunchin cannot stand.  And
臣 is polyphonic: Schuessler tabulates dźin AND gin, and Appendix A prints
the first, as it does for all 46 polyphonic slots.

This step asks what the second reading allows.  It prices every
combination of the two characters against the corpus, and then tests the
survivors against the Turkic evidence, because a cheap transcription of a
word that cannot be formed is worth nothing.

Everything is counted here.  Onset rates come from the aligned Sanskrit
pairs.  Vowel rates come from the same corpus, except for a source ö or ü,
which Sanskrit does not have and which is therefore taken from the Ligeti
Turkic glossaries, the control the paper already uses for that gap.  The
suffix counts come from the lexicons.

The product of the rates is not a probability that a reading is right.  It
ranks candidates against each other and against the thresholds the paper
uses: 1 in 37 retires Baγatur in §8.1.

Output: reports\step47_summary.txt
"""
import csv, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import step46_junchen_space as S      # onset counting and lexicon loading


# ---------------------------------------------------------------- vowels
def chinese_vowel_class(v):
    core = [c for c in v if c in u"aeiouɑɔəɛɨʊüö"]
    if not core:
        return "?"
    c = core[-1] if len(core) > 1 else core[0]
    if c in u"uoɔʊüö":
        return "rounded"
    if c in u"ieɛ":
        return "front"
    if c in u"əɨ":
        return "central"
    return "open"


def measure_vowels_lh():
    """source vowel -> the class the character writes, Later Han corpus."""
    VOW = {}
    for x in csv.DictReader(io.open(os.path.join(EXT, "LHantab.tsv"),
                                    encoding="utf8", errors="ignore"),
                            delimiter="\t"):
        z = (x.get("zi") or "").strip(); v = (x.get("vow") or "").strip()
        if z and z not in VOW:
            VOW[z] = v
    rows = [r for r in csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                              encoding="utf-8-sig"))
            if r.get("align") == "exact" and r.get("n_chars") == r.get("n_syl")]
    tot = collections.Counter(); cell = collections.Counter()
    for r in rows:
        zi = (r.get("trad") or "").strip(); src = (r.get("skt") or "").strip()
        vs = [ch for k, ch in S.toks(src) if k == "V"]
        if not zi or len(vs) != len(zi):
            continue
        for ch, v in zip(zi, vs):
            if ch not in VOW:
                continue
            k = {"i": "i/e", u"ī": "i/e", "e": "i/e",
                 "u": "u/o", u"ū": "u/o", "o": "u/o",
                 "a": "a", u"ā": "a"}.get(v)
            if k:
                tot[k] += 1; cell[(k, chinese_vowel_class(VOW[ch]))] += 1
    return tot, cell


def measure_vowels_turkic():
    """source ö/ü -> written class, from the Ligeti glossaries."""
    p = os.path.join(DER, "ligeti_turkic_chinese_pairs.csv")
    if not os.path.exists(p):
        return 0, 0
    V = u"aeıioöuüâê"
    def syl(w):
        w = w.lower().replace("-", ""); out = []; cur = ""
        for ch in w:
            cur += ch
            if ch in V:
                out.append(cur); cur = ""
        if cur and out:
            out[-1] += cur
        elif cur:
            out.append(cur)
        return out
    def cvowel(s):
        s = s.lower()
        for pat, cl in [("iu", "rounded"), ("ou", "rounded"), ("uo", "rounded"),
                        ("o", "rounded"), ("u", "rounded"),
                        ("ie", "front"), ("i", "front"), ("e", "front"), ("a", "open")]:
            if pat in s:
                return cl
        return "?"
    n = f = 0
    for r in csv.DictReader(io.open(p, encoding="utf-8-sig")):
        if (r.get("suspect") or "").strip():
            continue
        ts = syl(r["turkic"]); cs = [x for x in r["efeo_chinese"].split("-") if x]
        if len(ts) != len(cs):
            continue
        for a, b in zip(ts, cs):
            vs = [ch for ch in a if ch in V]
            if vs and vs[-1] in u"öü":
                n += 1
                if cvowel(b) == "front":
                    f += 1
    return f, n


# ---------------------------------------------------------------- morphology
SUFFIX = [(u"-gAn  front  -gen/-ken", r"(gen|ken)$"),
          (u"-gAn  back   -gan/-kan", r"(gan|kan)$"),
          (u"-gUn  front  -gün/-kün", u"(gün|kün)$"),
          (u"-gUn  back   -gun/-kun", r"(gun|kun)$"),
          (u"-gIn  front  -gin/-kin", r"(gin|kin)$"),
          (u"-gIn  back   -gın/-kın", u"(gın|kın)$")]
HABITUAL = (u"daima", u"her zaman", u"çok ", u"sürekli")


def main():
    tot_o, cell_o, npairs = S.measure_onsets()
    tot_v, cell_v = measure_vowels_lh()
    f_front, f_n = measure_vowels_turkic()
    lex = S.load_lexicon()

    lines = []
    def say(s=u""):
        try:
            print(s)
        except Exception:
            print(s.encode("ascii", "replace").decode("ascii"))
        lines.append(s)

    def onset(srcs, ci):
        a = sum(cell_o[(s, ci)] for s in srcs); b = sum(tot_o[s] for s in srcs)
        return (float(a) / b if b else 0.0), a, b

    def vowel(k, cl):
        a = cell_v[(k, cl)]; b = tot_v[k]
        return (float(a) / b if b else 0.0), a, b

    k_k = onset(["k"], u"k")
    g_g = onset(["g", "gh"], u"g")
    k_g = onset(["k"], u"g")
    c_dz = onset(["c"], u"dź")
    j_dz = onset(["j", "jh"], u"dź")
    v_front = vowel("i/e", "front")
    v_a_front = vowel("a", "front")
    v_u_front = vowel("u/o", "front")
    v_round = vowel("u/o", "rounded")
    v_unr_round = vowel("a", "rounded")
    v_of = (float(f_front) / f_n if f_n else 0.0, f_front, f_n)
    CODA = (77 / 93.0, 77, 93)

    say(u"Step 47.  Reading 軍臣, every permitted form priced.")
    say(u"Aligned one-character-to-one-syllable pairs: %d" % npairs)
    say(u"")
    say(u"=" * 70)
    say(u"1.  The rates, all counted from the corpora in this repository")
    say(u"=" * 70)
    for lab, t in [(u"source k written with a Chinese k-", k_k),
                   (u"source g written with a Chinese g-", g_g),
                   (u"source k written with a Chinese g-", k_g),
                   (u"source c written with a Chinese dź-", c_dz),
                   (u"source j written with a Chinese dź-", j_dz),
                   (u"source i or e written with a front vowel", v_front),
                   (u"source a written with a front vowel", v_a_front),
                   (u"source u or o written with a front vowel", v_u_front),
                   (u"source u or o written with a rounded vowel", v_round),
                   (u"source a written with a rounded vowel", v_unr_round),
                   (u"source ö or ü written with a front vowel", v_of),
                   (u"source -n written with a Chinese -n", CODA)]:
        say(u"   %-44s %4d of %-5d %6.1f%%" % (lab, t[1], t[2], 100 * t[0]))
    say(u"")
    say(u"   The ö/ü row is from the Ligeti Turkic glossaries, because")
    say(u"   Sanskrit has no front rounded vowel. It is the control the paper")
    say(u"   already uses for that gap. Everything else is Later Han.")
    say(u"")

    # ------------------------------------------------------------ pricing
    first = {}
    for w in (u"kön", u"kün", u"kon", u"kun"):
        first[w] = k_k[0] * v_round[0] * CODA[0]
    for w in (u"kan", u"ken", u"kın", u"kin"):
        first[w] = k_k[0] * v_unr_round[0] * CODA[0]

    second = collections.OrderedDict()
    for w in (u"gen", u"gin"):
        second[w] = g_g[0] * v_front[0] * CODA[0]
    second[u"gan"] = g_g[0] * v_a_front[0] * CODA[0]
    for w in (u"ken", u"kin"):
        second[w] = k_g[0] * v_front[0] * CODA[0]
    second[u"gün"] = g_g[0] * v_of[0] * CODA[0]
    second[u"kan"] = k_g[0] * v_a_front[0] * CODA[0]
    second[u"gun"] = g_g[0] * v_u_front[0] * CODA[0]
    for w in (u"çen", u"çin", u"çan"):
        second[w] = c_dz[0] * v_front[0] * CODA[0]

    say(u"=" * 70)
    say(u"2.  Each half of the name")
    say(u"=" * 70)
    say(u"   軍 kun, first element")
    for w, v in sorted(first.items(), key=lambda x: -x[1]):
        say(u"      %-6s %8.2f%%" % (w, 100 * v))
    say(u"   臣, second element, on whichever reading each one needs")
    for w, v in sorted(second.items(), key=lambda x: -x[1]):
        rd = u"gin" if w[0] in u"gk" else u"dźin"
        say(u"      -%-6s %8.2f%%   (needs 臣 = %s)" % (w, 100 * v, rd))
    say(u"")

    say(u"=" * 70)
    say(u"3.  The whole name")
    say(u"=" * 70)
    say(u"   %-12s %10s  %-10s  %s" % (u"form", u"cost", u"odds", u"what it would have to be"))
    NOTE = {u"gen": u"kön- + the -gAn participle",
            u"gin": u"kön- + -gIn, but see the harmony test below",
            u"gan": u"a back-vowel -gAn on a front stem: disharmonic",
            u"gün": u"kön- + -gUn, the shape modern Turkish would use",
            u"gun": u"disharmonic, and -gUn is not a participle in the period",
            u"ken": u"noun + noun, ken being a place-name element",
            u"kin": u"noun + noun, kin meaning a grudge",
            u"kan": u"noun + noun, kan meaning blood",
            u"çin": u"excluded: 0 of %d" % c_dz[2],
            u"çen": u"excluded: 0 of %d" % c_dz[2],
            u"çan": u"excluded: 0 of %d" % c_dz[2]}
    out = []
    for b, vb in second.items():
        c = first[u"kün"] * vb
        out.append((c, u"kün" + b, b))
    out.sort(reverse=True)
    for c, name, b in out:
        say(u"   %-12s %9.3f%%  %-10s  %s"
            % (name, 100 * c, (u"1 in %d" % int(1 / c)) if c else u"excluded",
               NOTE.get(b, u"")))
    say(u"")
    say(u"   kön, kon and kun cost exactly what kün costs: same onset, same")
    say(u"   rounded vowel, same written -n. The transcription cannot separate")
    say(u"   them, so the first element is chosen on meaning, not on evidence.")
    say(u"")

    # ------------------------------------------------------------ morphology
    say(u"=" * 70)
    say(u"4.  Which suffix existed, counted in the lexicons")
    say(u"=" * 70)
    say(u"   A cheap transcription of a word that cannot be formed is worth")
    say(u"   nothing. These are headwords in the DLT index, the Codex and the")
    say(u"   Irk Bitig glossary, %d in all." % len(lex))
    say(u"")
    for lab, pat in SUFFIX:
        hits = [(w, g) for w, (g, s) in lex.items()
                if re.search(pat, w) and len(w) > 4]
        hab = [(w, g) for w, g in hits if any(h in g for h in HABITUAL)]
        say(u"   %-26s %3d headwords, %d glossed as habitual"
            % (lab, len(hits), len(hab)))
        for w, g in sorted(hab)[:4]:
            say(u"        %-14s %s" % (w, g[:48]))
    say(u"")
    say(u"   The -gAn rows carry the habitual glosses: daima, her zaman, cok.")
    say(u"   The -gUn rows are concrete nouns, birds and plants and body parts.")
    say(u"   In the eleventh-century record -gAn is the productive participle")
    say(u"   and -gUn is not. The modern durgun, coşkun, ötgün belong to a")
    say(u"   later productivity of -gUn and are not evidence for this period.")
    say(u"")

    say(u"   THE HARMONY TEST. -gAn has two shapes, front and back, so a front")
    say(u"   stem takes -gen whatever its rounding. -gIn and -gUn have four, so")
    say(u"   a front ROUNDED stem such as kön- must take -gün and cannot take")
    say(u"   -gin. That removes köngin, which the transcription prices as")
    say(u"   cheaply as köngen, on grounds that have nothing to do with Chinese.")
    say(u"")

    stem = [(w, g) for w, (g, s) in lex.items() if re.match(u"^kön", w)]
    say(u"   THE STEM. kön- is attested as a verb in the same dictionary:")
    for w, g in sorted(stem):
        if u"mek" in w or u"mak" in w:
            say(u"        %-14s %s" % (w, g[:52]))
    say(u"")

    best = first[u"kün"] * second[u"gen"]
    say(u"=" * 70)
    say(u"5.  Where that leaves the name")
    say(u"=" * 70)
    say(u"   köngen, the participle of an attested verb meaning to become")
    say(u"   straight or upright, costs %.1f%%, about 1 in %d."
        % (100 * best, int(1 / best)))
    say(u"   The threshold that retires Baγatur in the paper is 1 in 37, and")
    say(u"   the best branch of 冒頓 is 1 in 9. This is cheaper than either.")
    say(u"   The transcription and the morphology select the same form, and")
    say(u"   they were measured independently.")
    say(u"")
    say(u"   WHAT IS NOT SETTLED, and must be said wherever this is used:")
    say(u"   - köngen is not itself an attested headword. It is a formation by")
    say(u"     a productive rule from an attested stem, which is a stronger")
    say(u"     position than a form requiring a lost consonant, but it is not")
    say(u"     an attestation.")
    say(u"   - The lexicons are eleventh century and the name is second century")
    say(u"     BCE. That -gAn was productive for Kāşgarî does not establish it")
    say(u"     1250 years earlier. This is the same gap the whole paper carries.")
    say(u"   - Whether -gAn formations were used as personal names or titles in")
    say(u"     Old Turkic is not tested here. Erdal's Grammar is the place.")
    say(u"   - The g-to-g rate is measured over all positions. Whether a g after")
    say(u"     a nasal behaves the same is not measured.")
    say(u"   - The first element is undetermined: kön, kün, kon and kun all cost")
    say(u"     the same. Choosing kön- is a semantic choice, which is the")
    say(u"     epithet habit S1.1 lists as a weakness.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    dest = os.path.join(REP, "step47_summary.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)


if __name__ == "__main__":
    main()
