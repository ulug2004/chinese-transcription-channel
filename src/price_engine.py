# -*- coding: utf-8 -*-
r"""
price_engine.  One scorer for every row of the record.

Until now each priced row in the supplement had its own hand-written
calculation, in steps 47 to 55, each making its own choices about which
rates applied.  Sixteen rows had no figure at all.  This module replaces
all of that with a single function: characters plus a proposed reading in,
a price out, computed the same way for every row.

THE MODEL.  Each Chinese character takes one of four roles.

    SYL    it writes one Turkic syllable
    SYL2   it writes two, its written stop coda carrying the second onset
           (compression, 93 of 1,017 pairs, 47 of them by this device)
    CONS   it writes a bare consonant, its vowel writing nothing
           (the final-character device, 91 of 199 in the Ligeti corpus)
    NULL   it writes nothing at all

An alignment is an assignment of roles that consumes every Turkic syllable.
Every alignment is enumerated and the CHEAPEST is reported, which is the
correct rule: we are asking what the transcription could be doing, not what
we would like it to be doing.

EVERY RATE IS MEASURED, and every cell that is not is flagged.  A price
that rests on an unmeasured cell is reported with the count of such cells
beside it, so a reader can discount it.

The product is not a probability that a reading is right.  It ranks
candidates against each other and against thresholds the paper already
uses: 1 in 37 retires Baγatur in §8.1.
"""
import csv, io, os, re, sys, collections, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
sys.path.insert(0, HERE)
import step46_junchen_space as S

TV = u"aeıioöuüâêîôāēīōū"
BACK = set(u"aıouâ")

# Turkic letter -> the Sanskrit source symbols it is counted as
# A Turkic phoneme answers to every Sanskrit phoneme that merges into it.
# Turkic has one dental stop series where Sanskrit has dental and retroflex,
# one sibilant pair where Sanskrit has three, and no palatal nasal at all.
# Mapping narrowly produced zeros that were artefacts of that asymmetry.
SRCMAP = {u"h": ["h"], u"k": ["k", "kh"], u"g": ["g", "gh"], u"q": ["k", "kh"],
          u"x": ["h"],
          u"t": ["t", "th", u"ṭ", u"ṭh"], u"d": ["d", "dh", u"ḍ", u"ḍh"],
          u"ç": ["c", "ch"], u"c": ["j", "jh"], u"j": ["j", "jh"],
          u"ñ": [u"ṅ"], u"ŋ": [u"ṅ"], u"n": ["n", u"ṇ"], u"y": ["y"],
          u"m": ["m"],
          u"ş": [u"ś", u"ṣ"], u"s": ["s", u"ṣ"], u"z": ["s"],
          u"l": ["l"], u"r": ["r"],
          u"b": ["b", "bh", "v"], u"p": ["p", "ph"],
          u"v": ["v", "b"], u"w": ["v"], u"f": ["p", "ph"]}

# Turkic coda -> the source coda row of the coda table
CODAMAP = {u"p": "p", u"b": "p", u"t": "t", u"d": "t",
           u"k": "k", u"g": "k", u"q": "k", u"ğ": "k",
           u"m": "m", u"n": "n", u"ñ": u"ŋ", u"ŋ": u"ŋ",
           u"l": "L", u"r": "L",
           # Later Han has no sibilant coda at all, so a source -ş/-s/-z can
           # only be left open or carried by some other coda.  Step 20's table
           # has no sibilant row; step 37's class table does, and _sibilant()
           # below reads it.  Without this row every reading ending in -ş was
           # unpriceable and the engine silently fell back on a more expensive
           # alignment: karındaş, çarvuş and toğrulmış were all affected.
           u"ş": "S", u"s": "S", u"z": "S"}
CPLACE = {"p": "labial", "m": "labial", "t": "dental", "n": "dental",
          "k": "velar", u"ŋ": "velar"}
TPLACE = {u"p": "labial", u"b": "labial", u"m": "labial",
          u"t": "dental", u"d": "dental", u"n": "dental",
          u"k": "velar", u"g": "velar", u"q": "velar", u"ğ": "velar",
          u"ñ": "velar", u"ŋ": "velar"}


# ----------------------------------------------------------------- corpus
class Rates(object):
    def __init__(self, extra_pairs=None):
        self.extra = extra_pairs or []
        self._onsets()
        self._vowels()
        self._codas()
        self._sibilant()
        self._shapes()
        self._devices()
        self.ALLREAD = all_readings()
        self.missing = collections.Counter()

    def _pairs(self, aligned_only=True):
        rows = list(csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                           encoding="utf-8-sig"))) + list(self.extra)
        if aligned_only:
            rows = [r for r in rows
                    if r.get("align") == "exact" and r.get("n_chars") == r.get("n_syl")]
        return rows

    def _lh(self):
        INI, VOW = {}, {}
        for x in csv.DictReader(io.open(os.path.join(EXT, "LHantab.tsv"),
                                        encoding="utf8", errors="ignore"), delimiter="\t"):
            z = (x.get("zi") or "").strip()
            if z and z not in INI:
                INI[z] = (x.get("con") or "").strip()
                VOW[z] = (x.get("vow") or "").strip()
        return INI, VOW

    def _onsets(self):
        INI, _V = self._lh()
        self.INI = INI
        tot = collections.Counter(); cell = collections.Counter()
        vi = collections.Counter()
        for r in self._pairs():
            zi = (r.get("trad") or "").strip(); src = (r.get("skt") or "").strip()
            on = S.onsets(src)
            if not zi or len(on) != len(zi):
                continue
            for ch, so in zip(zi, on):
                if ch not in INI:
                    continue
                if not so:
                    vi[INI[ch]] += 1
                    continue
                tot[so] += 1; cell[(so, INI[ch])] += 1
        self.o_tot, self.o_cell, self.vi = tot, cell, vi
        self.n_pairs = len(self._pairs())

    def _vowels(self):
        _I, VOW = self._lh()
        self.VOW = VOW
        tot = collections.Counter(); cell = collections.Counter()
        for r in self._pairs():
            zi = (r.get("trad") or "").strip(); src = (r.get("skt") or "").strip()
            vs = [c for k, c in S.toks(src) if k == "V"]
            if not zi or len(vs) != len(zi):
                continue
            for ch, v in zip(zi, vs):
                if ch not in VOW:
                    continue
                k = {"i": "i/e", u"ī": "i/e", "e": "i/e",
                     "u": "u/o", u"ū": "u/o", "o": "u/o",
                     "a": "a", u"ā": "a"}.get(v)
                if k:
                    tot[k] += 1; cell[(k, vclass(VOW[ch]))] += 1
        self.v_tot, self.v_cell = tot, cell
        # a Turkic ö/ü, which Sanskrit has no instance of: Ligeti control
        n = collections.Counter()
        p = os.path.join(DER, "ligeti_turkic_chinese_pairs.csv")
        if os.path.exists(p):
            def syl(w):
                w = w.lower().replace("-", ""); out = []; cur = ""
                for ch in w:
                    cur += ch
                    if ch in TV:
                        out.append(cur); cur = ""
                if cur and out:
                    out[-1] += cur
                elif cur:
                    out.append(cur)
                return out
            def cv(t):
                t = t.lower()
                for pat, cl in [("iu", "rounded"), ("ou", "rounded"), ("uo", "rounded"),
                                ("o", "rounded"), ("u", "rounded"), ("ie", "front"),
                                ("i", "front"), ("e", "front"), ("a", "open")]:
                    if pat in t:
                        return cl
                return "?"
            for r in csv.DictReader(io.open(p, encoding="utf-8-sig")):
                if (r.get("suspect") or "").strip():
                    continue
                ts = syl(r["turkic"]); cs = [x for x in r["efeo_chinese"].split("-") if x]
                if len(ts) != len(cs):
                    continue
                for a, b in zip(ts, cs):
                    vv = [c for c in a if c in TV]
                    if vv and vv[-1] in u"öü":
                        n[cv(b)] += 1
        self.ou = n

    def _codas(self):
        n = collections.Counter(); by = collections.Counter()
        for r in csv.DictReader(io.open(os.path.join(DER, "coda_spelling.csv"),
                                        encoding="utf-8-sig")):
            c = (r.get("source_coda") or "").strip()
            cc = (r.get("chinese_coda") or "").strip()
            k = int(r.get("count") or 0)
            n[c] += k
            by[(c, "open" if cc.startswith("open") else cc)] += k
        self.c_tot, self.c_cell = n, by
        rows = list(csv.DictReader(io.open(os.path.join(DER, "liquid_coda.csv"),
                                           encoding="utf-8-sig")))
        key = [k for k in rows[0] if k and "chinese_coda" in k][0]
        self.liq_open = sum(1 for r in rows if (r.get(key) or "").strip() == "open")
        self.liq_tot = len(rows)

    def _shapes(self):
        rows = list(csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                           encoding="utf-8-sig"))) + list(self.extra)
        d = collections.Counter()
        for r in rows:
            try:
                a, b = int(r.get("n_chars") or 0), int(r.get("n_syl") or 0)
            except Exception:
                continue
            if a and b:
                d[a - b] += 1
        self.shape = d
        self.shape_n = sum(d.values())

    def _sibilant(self):
        """How a source sibilant coda was written, from step 37's class table.

        Reported as a Counter over the written class, so that a character
        which carries a dental stop is priced on the cell that actually
        measures that substitution rather than on the residue."""
        import step37_coda_manner as S37
        lh = S37.lh_first()
        n = collections.Counter()
        for row in S37.rd(os.path.join(DER, "nti_transcription_pairs.csv")):
            chars = [c for c in (row.get("trad") or "") if u"\u3400" <= c <= u"\u9fff"]
            units = S37.parse(row.get("skt") or "")
            if not chars or len(chars) != len(units):
                continue
            for ch, (_v, coda) in zip(chars, units):
                if S37.s_class(coda) != "sibilant":
                    continue
                vw = lh.get(ch)
                if not vw:
                    continue
                n[S37.w_class(S37.written_coda(vw))] += 1
        self.sib = n
        self.sib_n = sum(n.values())

    SIBCLASS = {u"": "open", u"t": "dental stop", u"n": "dental nasal",
                u"k": "velar stop", u"\u014b": "velar nasal",
                u"p": "labial stop", u"m": "labial nasal"}

    def sibilant(self, cchar_coda):
        if not self.sib_n:
            return None, "unmeasured"
        cls = self.SIBCLASS.get(cchar_coda or u"")
        if cls is None:
            return None, "unmeasured"
        return float(self.sib[cls]) / self.sib_n, "measured(37)"

    def _devices(self):
        import step52_final_consonant as S52
        n, _o, _e = S52.turkic_finals()
        d = n["of those, with an EXTRA final character"] if n else 0
        self.device = (float(n["  the extra character writes that consonant"]) / d) if d else None
        import step49_clanname as C49
        tv = C49.turkic_velars()
        b = sum(v for (c, i), v in tv.items() if c == u"back q") if tv else 0
        self.q_h = (float(tv[(u"back q", u"h-")]) / b) if b else None

    # ---------------------------------------------------------- accessors
    def onset(self, tlet, cini, back=False):
        # tlet must be tested for emptiness first: in Python "" is a substring
        # of every string, so `tlet in u"kqgğ"` is TRUE for the empty onset that
        # marks a vowel-initial syllable.  Without the guard, every vowel-initial
        # syllable on an h-, ɣ- or x- character in a back-vowel word was priced
        # at the §8.5 rate of 65.2% instead of the measured 0 of 140, which is
        # the exact cell this file uses to retire readings elsewhere.
        if tlet and cini in u"hɣx" and tlet in u"kqgğ" and back and self.q_h:
            return self.q_h, "measured(8.5)"
        if tlet == u"":                                    # vowel-initial syllable
            t = sum(self.vi.values())
            return ((float(self.vi.get(cini, 0)) / t) if t else 0.0), "measured"
        srcs = SRCMAP.get(tlet)
        if not srcs:
            return None, "unmapped"
        a = sum(self.o_cell[(s, cini)] for s in srcs)
        b = sum(self.o_tot[s] for s in srcs)
        if not b:
            return None, "unmeasured"
        if a == 0:
            # A zero means one of two very different things. If this Chinese
            # initial is the regular vehicle for some OTHER source phoneme,
            # then Sanskrit always had an exact match available and never had
            # to make this substitution: the corpus did not test it, and the
            # zero is an inventory gap, not evidence of a ban. If nothing
            # much goes to this initial, the zero is a real absence.
            got = sum(v for (so, ci), v in self.o_cell.items() if ci == cini)
            best = max([v for (so, ci), v in self.o_cell.items() if ci == cini] or [0])
            if got and best >= 5:
                return 0.0, "zero(inventory gap)"
            return 0.0, "zero(contested)"
        return float(a) / b, "measured"

    def vowel(self, tv_, ccls):
        if tv_ in u"öü":
            t = sum(self.ou.values())
            if not t or ccls not in self.ou:
                # the Ligeti classifier emits rounded, front and open only, so
                # a central character is outside what this control can measure
                return None, "unmeasured(no Ligeti cell)"
            return float(self.ou[ccls]) / t, "measured(Ligeti)"
        k = {u"a": "a", u"â": "a", u"e": "i/e", u"i": "i/e", u"ı": "i/e",
             u"o": "u/o", u"u": "u/o"}.get(tv_)
        if not k or not self.v_tot[k]:
            return None, "unmeasured"
        return float(self.v_cell[(k, ccls)]) / self.v_tot[k], "measured"

    def coda(self, tcoda, cchar_coda, nxt_onset=None):
        """Cost of a Turkic coda given what the character actually writes."""
        if not tcoda and not cchar_coda:
            return 1.0, "measured"
        row = CODAMAP.get(tcoda)
        if row == "S" and tcoda:
            return self.sibilant(cchar_coda)
        if tcoda and not cchar_coda:                       # unwritten
            if row == "L":
                return float(self.liq_open) / self.liq_tot, "measured"
            if row and self.c_tot[row]:
                return float(self.c_cell[(row, "open")]) / self.c_tot[row], "measured"
            return None, "unmeasured"
        if tcoda and cchar_coda:
            if row == "L":
                return (1.0 - float(self.liq_open) / self.liq_tot), "measured"
            if row and self.c_tot[row]:
                if TPLACE.get(tcoda) == CPLACE.get(cchar_coda):
                    return float(self.c_cell[(row, cchar_coda)]) / self.c_tot[row], "measured"
                same = sum(v for (a, b), v in self.c_cell.items()
                           if a == row and b != "open" and b != row)
                return (float(same) / self.c_tot[row]) if self.c_tot[row] else None, "measured"
            return None, "unmeasured"
        # character carries a written coda the Turkic syllable does not have:
        # it may be writing the NEXT onset (the junction), else it is unexplained
        if nxt_onset and TPLACE.get(nxt_onset) == CPLACE.get(cchar_coda):
            return self.junction(), "measured"
        return 0.02, "assumed"

    def junction(self):
        return 165 / 446.0            # step 22: a medial written coda writes the next onset

    def compression(self):
        d = self.shape.get(-1, 0) + self.shape.get(-2, 0)
        return (float(d) / self.shape_n) if self.shape_n else None

    def spare_one(self):
        return (float(self.shape.get(1, 0)) / self.shape_n) if self.shape_n else None

    def spare_more(self):
        m = sum(v for k, v in self.shape.items() if k >= 2)
        return (float(m) / self.shape_n) if self.shape_n else 0.0


def vclass(v):
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


# ------------------------------------------------------------ the strings
def parse_lh(s):
    """'hɑ tɑ ńə' -> [(onset, vowelclass, coda), ...]"""
    out = []
    for tok in s.split():
        tok = tok.strip(u"ᴬᴮᶜ")
        m = re.match(u"^([^aeiouɑɔəɛɨʊüöāēī]*)(.*)$", tok)
        on = m.group(1); rest = m.group(2)
        coda = ""
        if rest and rest[-1] in u"ptkmnŋ":
            coda = rest[-1]; rest = rest[:-1]
        out.append((on, vclass(rest), coda, tok))
    return out


def syllabify(w):
    """Turkic syllabification: one intervocalic consonant onsets the next
    syllable, two or more split, with the first closing the previous one."""
    w = w.lower()
    if not any(c in TV for c in w):
        return None
    pos = [i for i, c in enumerate(w) if c in TV]
    syls = []
    for n, i in enumerate(pos):
        start = 0 if n == 0 else None
        if n == 0:
            onset = w[:i]
        else:
            gap = w[pos[n - 1] + 1:i]
            onset = gap[1:] if len(gap) >= 2 else gap
        end = pos[n + 1] if n + 1 < len(pos) else len(w)
        if n + 1 < len(pos):
            gap = w[i + 1:pos[n + 1]]
            coda = gap[:1] if len(gap) >= 2 else ""
        else:
            coda = w[i + 1:]
        syls.append((onset, w[i], coda))
    return syls


def syllabify_all(w, cap=6):
    """Every way of dividing the intervocalic clusters of one word.

    syllabify() takes one choice: the first consonant of a cluster closes the
    previous syllable and the rest onset the next.  For a two-consonant cluster
    that is the only sensible split, but for three it is not, and the choice
    decides whether a reading can be priced at all.  korklu came out as
    kor + klu, whose kl- onset has no cell, when the analysis the entry argues
    is kork + lu, with the -rk written by one character.  Rather than prefer one
    rule, generate the splits and let the cheapest alignment choose, exactly as
    the engine already does for a written <ng> and for a polyphonic character.
    """
    w = w.lower()
    if not any(c in TV for c in w):
        return []
    pos = [i for i, c in enumerate(w) if c in TV]
    gaps = []
    for n in range(len(pos) - 1):
        gaps.append(w[pos[n] + 1:pos[n + 1]])
    choices = []
    for g in gaps:
        if len(g) <= 1:
            # nothing to decide: a single intervocalic consonant onsets the
            # next syllable and closes nothing, which is the Turkic rule and
            # what syllabify() has always done.  Writing len(g) here instead
            # of 0 made every such consonant a coda, left the next syllable
            # vowel-initial, and broke eighteen rows at once.
            choices.append([0])
        else:
            # at least one consonant onsets the next syllable, so the split
            # runs from one closing to all-but-one closing.  The first entry
            # reproduces syllabify() exactly.
            choices.append(list(range(1, len(g))))
    outs = []
    for combo in itertools.product(*choices) if choices else [()]:
        syls = []
        for n, i in enumerate(pos):
            onset = w[:i] if n == 0 else gaps[n - 1][combo[n - 1]:]
            coda = gaps[n][:combo[n]] if n < len(gaps) else w[i + 1:]
            syls.append((onset, w[i], coda))
        if syls not in outs:
            outs.append(syls)
        if len(outs) >= cap:
            break
    return outs


def reading_syllables(reading, which=0):
    """A reading may be several words; returns a flat syllable list.

    `which` selects among the cluster splits of syllabify_all; 0 reproduces the
    old behaviour exactly, so every caller that does not ask for a variant sees
    what it always saw."""
    words = [x for x in re.split(u"[ \\-]+", reading.strip()) if x]
    out = []
    for w in words:
        alts = syllabify_all(w)
        if not alts:
            return None
        out.extend(alts[which] if which < len(alts) else alts[0])
    return out


def reading_syllable_sets(reading):
    """All flat syllable lists for a reading, cheapest-first order not implied."""
    words = [x for x in re.split(u"[ \\-]+", reading.strip()) if x]
    per = []
    for w in words:
        alts = syllabify_all(w)
        if not alts:
            return []
        per.append(alts)
    sets = []
    for combo in itertools.product(*per):
        flat = []
        for s in combo:
            flat.extend(s)
        if flat not in sets:
            sets.append(flat)
        if len(sets) >= 12:
            break
    return sets


# ------------------------------------------------------------- the scorer
TITLE_CHARS  = u"若鞮"       # the title element argued once in §9
TITLE_READING = u"inakt"

def norm_reading(r):
    """Turkish casing, done before lower(): Python maps \u0130 to i plus a
    combining dot, which then matches nothing."""
    r = r.replace(u"\u0130", u"i").replace(u"I", u"\u0131")
    return r.strip().lower().replace(u"\u0307", u"")


def reading_variants(r):
    """A written <ng> is either a velar nasal or n followed by g, and no rule
    decides which: Tunga has one segment, Köngen has two. Both parses are
    offered and the cheapest alignment chooses, as with a polyphonic
    character or a diphthong."""
    r = norm_reading(r)
    outs = [r]
    idx = [i for i in range(len(r) - 1) if r[i:i + 2] == u"ng"]
    for k in range(1, 2 ** len(idx)):
        v = list(r); drop = []
        for b, i in enumerate(idx):
            if k >> b & 1:
                v[i] = u"\u014b"; drop.append(i + 1)
        for i in sorted(drop, reverse=True):
            del v[i]
        outs.append(u"".join(v))
    return outs


def char_variants(ch, INI, ALL):
    """Every Later Han reading tabulated for a character, each expanded over
    the vowel classes its nucleus can present.  A diphthong such as ui can
    write either component, so both are offered and the cheapest alignment
    decides, which is the same rule used everywhere else here."""
    out = []
    for con, vow in ALL.get(ch, []):
        v = vow.strip(u"\u1d2c\u1d2e\u1d9c")
        coda = ""
        if v and v[-1] in u"ptkmn\u014b":
            coda = v[-1]; v = v[:-1]
        cores = [c for c in v if c in u"aeiou\u0251\u0254\u0259\u025b\u0268\u028a\u00fc\u00f6"]
        classes = []
        for c in (cores or [""]):
            cl = vclass(c)
            if cl not in classes:
                classes.append(cl)
        for cl in classes:
            out.append((con, cl, coda, con + vow))
    return out or [("", "?", "", ch)]


VARIANT = {}          # traditional form -> the shape the table actually carries


def all_readings():
    ALL = collections.defaultdict(list)
    for x in csv.DictReader(io.open(os.path.join(EXT, "LHantab.tsv"),
                                    encoding="utf8", errors="ignore"), delimiter="\t"):
        z = (x.get("zi") or "").strip()
        if not z:
            continue
        v = ((x.get("con") or "").strip(), (x.get("vow") or "").strip())
        if v not in ALL[z]:
            ALL[z].append(v)
    # Schuessler's table carries four of the record's characters only in
    # their simplified shape, which left those rows unpriceable. The
    # traditional form is mapped onto it and the substitution recorded in
    # VARIANT so it stays visible.  Schuessler's table carries one shape of
    # each of these pairs and the record uses the other, in BOTH directions:
    # for 户 虚 禄 脱 the table has the simplified shape, for 撐 犁 the
    # traditional one.  An earlier note here said 撑 was absent in both
    # shapes; that was wrong.  U+6491 撑 is absent but U+6490 撐 is present
    # with the reading ḍaŋ, so the row prices once the two are folded.
    PAIRS = ((u"\u6236", u"\u6237"),   # 戶 户
             (u"\u865b", u"\u865a"),   # 虛 虚
             (u"\u797f", u"\u7984"),   # 祿 禄
             (u"\u812b", u"\u8131"),   # 脫 脱
             (u"\u6491", u"\u6490"),   # 撑 撐
             (u"\u645a", u"\u6490"),   # 摚 撐, the Hou Hanshu's shape
             (u"\u7282", u"\u7281"),   # 犂 犁, likewise
             (u"\u79bf", u"\u79c3"))   # 禿 秃, needed for the Jie couplet
    for a, b in PAIRS:
        if a not in ALL and b in ALL:
            ALL[a] = list(ALL[b]); VARIANT[a] = b
        elif b not in ALL and a in ALL:
            ALL[b] = list(ALL[a]); VARIANT[b] = a
    return ALL


def syl_cost(R, variant, syl, nxt_syl, next_is_cons, back):
    """Cost of one character writing one Turkic syllable. Returns
    (price, flags) with price None when a needed cell is unmeasured."""
    con, cvc, ccd, raw = variant
    on, vw, cd = syl
    fl = collections.Counter()
    r1, f1 = R.onset(on, con, back); fl[f1] += 1
    r2, f2 = R.vowel(vw, cvc);       fl[f2] += 1
    if r1 is None or r2 is None:
        return None, fl
    p = r1 * r2
    if cd and not next_is_cons:
        for k, letter in enumerate(cd):
            nxt_on = nxt_syl[0] if nxt_syl else None
            r3, f3 = R.coda(letter, ccd if k == 0 else "", nxt_on)
            fl[f3] += 1
            if r3 is None:
                return None, fl
            p *= r3
            if len(cd) > 1:
                fl["cluster coda"] += 1
    elif not cd and ccd:
        nxt_on = nxt_syl[0] if nxt_syl else None
        r3, f3 = R.coda("", ccd, nxt_on); fl[f3] += 1
        if r3 is None:
            return None, fl
        p *= r3
    return p, fl


class Align(object):
    def __init__(self, price, roles, detail, flags, nsyl, nchar):
        self.price, self.roles, self.detail = price, roles, detail
        self.flags, self.nsyl, self.nchar = flags, nsyl, nchar
    @property
    def per_char(self):
        return self.price ** (1.0 / self.nchar) if self.nchar else 0.0


def price_name(chinese, reading, R, ALL=None, strip_title=True):
    """Cheapest alignment of a reading onto a character string."""
    ALL = ALL or R.ALLREAD
    zi = [c for c in chinese.strip() if c.strip()]
    note = u""
    rd0 = norm_reading(reading)
    if strip_title and len(zi) > 2 and "".join(zi[-2:]) == TITLE_CHARS \
            and TITLE_READING in rd0:
        zi = zi[:-2]
        rd0 = re.sub(TITLE_READING, u"", rd0).strip(u" -")
        note = u"title element " + TITLE_CHARS + u" excluded, argued once in \u00a79"
    if not zi or len(zi) > 9:
        return None, u"too long", note
    cands = []
    for rv in reading_variants(rd0):
        for sy in reading_syllable_sets(rv):
            if sy and (rv, sy) not in cands:
                cands.append((rv, sy))
    if not cands:
        return None, u"could not syllabify", note
    var = [char_variants(c, R.INI, ALL) for c in zi]
    if any(v[0][1] == "?" for v in var):
        miss = [c for c, v in zip(zi, var) if v[0][1] == "?"]
        return None, u"no Later Han reading for %s" % u" ".join(miss), note
    n = len(zi); best = None; blocked = []; unmet = []
    for _rv, syls in cands:
      for combo in itertools.product("SDCN", repeat=n):
          if sum({"S": 1, "D": 2, "C": 0, "N": 0}[r] for r in combo) != len(syls):
              continue
          if combo[0] == "C" or sum(1 for r in combo if r == "N") > 1:
              continue
          p = 1.0; det = []; fl = collections.Counter(); j = 0; ok = True
          zero = False; zeroname = u""
          back = any(v in BACK for _o, v, _c in syls)
          for i, role in enumerate(combo):
              if role == "N":
                  v = R.spare_one()
                  p *= v; fl["spare character"] += 1
                  det.append(u"%s writes nothing %.1f%%" % (zi[i], 100 * v)); continue
              if role == "C":
                  prev = syls[j - 1] if j else None
                  if not prev or not prev[2]:
                      ok = False; break
                  letter = prev[2][-1]; bestc = None
                  for con, cvc, ccd, raw in var[i]:
                      r1, f1 = R.onset(letter, con, back)
                      if r1 and (bestc is None or r1 > bestc[0]):
                          bestc = (r1, raw, f1)
                  if not bestc or R.device is None:
                      ok = False; break
                  p *= bestc[0] * R.device; fl["device"] += 1; fl[bestc[2]] += 1
                  det.append(u"%s writes -%s %.0f%% x device %.0f%%"
                             % (bestc[1], letter, 100 * bestc[0], 100 * R.device)); continue
              nxt_c = (i + 1 < n and combo[i + 1] == "C")
              nxt_s = syls[j + 1] if j + 1 < len(syls) else None
              bestv = None
              for v in var[i]:
                  if role == "D":
                      comp = R.compression()
                      if not comp or not v[2] or TPLACE.get(nxt_s[0]) != CPLACE.get(v[2]):
                          continue
                      q, f = syl_cost(R, (v[0], v[1], "", v[3]), syls[j], None, True, back)
                      if q is None:
                          continue
                      q *= comp; f["compression"] += 1
                  else:
                      q, f = syl_cost(R, v, syls[j], nxt_s, nxt_c, back)
                      if q is None:
                          continue
                  if bestv is None or q > bestv[0]:
                      bestv = (q, v[3], f)
              if bestv is None:
                  unmet.append(u"%s writing %s%s%s" % (zi[i], syls[j][0], syls[j][1], syls[j][2]))
                  ok = False; break
              if bestv[0] == 0:
                  zero = True
                  zeroname = u"%s writing %s (%s)" % (
                      zi[i], syls[j][0] + syls[j][1] + syls[j][2],
                      [k for k in bestv[2] if k.startswith("zero")][0]
                      if [k for k in bestv[2] if k.startswith("zero")] else u"zero")
              p *= bestv[0]; fl.update(bestv[2])
              det.append(u"%s=%s%s%s" % (bestv[1], syls[j][0], syls[j][1], syls[j][2]))
              j += 2 if role == "D" else 1
          if not ok:
              continue
          if zero or p == 0:
              blocked.append(zeroname or u"a measured zero"); continue
          a = Align(p, "".join(combo), u"  ".join(det), fl, len(syls), n)
          if best is None or p > best.price:
              best = a
    if best is None:
        if blocked:
            return None, u"blocked: " + blocked[0], note
        if unmet:
            seen = []
            for u_ in unmet:
                if u_ not in seen:
                    seen.append(u_)
            return None, u"no rate for " + u"; ".join(seen[:3]), note
        return None, u"no alignment consumes the reading", note
    return best, u"", note
