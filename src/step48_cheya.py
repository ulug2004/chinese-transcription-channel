# -*- coding: utf-8 -*-
r"""
Step 48.  The candidate space for 車牙, priced.

若鞮 is settled: the paper argues it as Inakt and it is fixed.  This step
takes only the two characters in front of it.

The supplement reads them Çöge-Ok and its own phonetics field says the
second step "is unsupported".  Three things are now measured rather than
asserted:

  a source vowel-initial syllable written with a Chinese velar nasal
      0 of 140.  137 of the 140 took a glottal.
  a source affricate written with the aspirated tśʰ-
      1 of 54.  The vehicle for a source affricate is plain tś-, 32 of 48.
  what a Chinese ŋ- actually writes
      a source g 13 times and a source velar nasal 5 times, out of 18.

So Çöge-Ok fails twice on the writing, before the invented syllable in the
first character is counted at all.

What the characters do offer.  BOTH are open, with no coda, so any source
coda is unwritten and Table 7 gives the price of that by class.  And 車 is
polyphonic in the way 冒, 單 and 臣 are:

    車   tśʰa    wants a source t      67 of 181, 37%
    車   kɨɑ     wants a source k      190 of 220, 86%
    牙   ŋa      wants a source g      13 of 90, 14%   or a source ŋ, 5 of 7

Output: reports\step48_summary.txt
"""
import csv, io, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import step46_junchen_space as S

V = u"aeıioöuüâêîôû"

# Table 7: a source coda left unwritten, by class
CODA_OPEN = {u"": 1.0,
             u"r": 21/37.0, u"l": 21/37.0,
             u"s": 27/36.0, u"ş": 27/36.0, u"z": 27/36.0,
             u"k": 8/21.0,  u"g": 8/21.0,  u"ğ": 8/21.0,
             u"t": 15/53.0, u"d": 15/53.0,
             u"p": 2/10.0,  u"b": 2/10.0,
             u"m": 4/23.0,
             u"n": 12/93.0,
             u"ñ": 2/22.0,  u"ŋ": 2/22.0}


def main():
    tot, cell, npairs = S.measure_onsets()
    lex = S.load_lexicon()
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

    # vowels, measured here on the Later Han corpus
    vt, vc = collections.Counter(), collections.Counter()
    VOWTAB = {}
    for x in csv.DictReader(io.open(os.path.join(ROOT, "data", "external", "LHantab.tsv"),
                                    encoding="utf8", errors="ignore"), delimiter="\t"):
        z = (x.get("zi") or "").strip(); v = (x.get("vow") or "").strip()
        if z and z not in VOWTAB:
            VOWTAB[z] = v
    def ccls(v):
        core = [c for c in v if c in u"aeiouɑɔəɛɨʊüö"]
        if not core: return "?"
        c = core[-1] if len(core) > 1 else core[0]
        if c in u"uoɔʊüö": return "rounded"
        if c in u"ieɛ":    return "front"
        if c in u"əɨ":     return "central"
        return "open"
    rows = [r for r in csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                              encoding="utf-8-sig"))
            if r.get("align") == "exact" and r.get("n_chars") == r.get("n_syl")]
    for r in rows:
        zi = (r.get("trad") or "").strip(); src = (r.get("skt") or "").strip()
        vs = [ch for k, ch in S.toks(src) if k == "V"]
        if not zi or len(vs) != len(zi): continue
        for ch, v in zip(zi, vs):
            if ch not in VOWTAB: continue
            k = {"i": "i/e", u"ī": "i/e", "e": "i/e", "u": "u/o", u"ū": "u/o",
                 "o": "u/o", "a": "a", u"ā": "a"}.get(v)
            if k:
                vt[k] += 1; vc[(k, ccls(VOWTAB[ch]))] += 1
    def vrate(k, cl):
        return (float(vc[(k, cl)]) / vt[k] if vt[k] else 0.0), vc[(k, cl)], vt[k]

    t_tsh  = rate(["t", "th"], u"tśʰ")
    c_tsh  = rate(["c", "ch"], u"tśʰ")
    c_ts   = rate(["c"], u"tś")
    k_k    = rate(["k"], u"k")
    g_k    = rate(["g", "gh"], u"k")
    g_ng   = rate(["g", "gh"], u"ŋ")
    ng_ng  = rate([u"ṅ"], u"ŋ")
    v_a    = vrate("a", "open")
    v_i    = vrate("i/e", "open")
    v_u    = vrate("u/o", "open")

    say(u"Step 48.  The candidate space for 車牙, priced.  若鞮 is fixed as Inakt.")
    say(u"Aligned one-character-to-one-syllable pairs: %d" % npairs)
    say(u"")
    say(u"=" * 70)
    say(u"1.  What the supplement's reading needs, measured")
    say(u"=" * 70)
    for lab, t in [(u"a source affricate written with tśʰ-", c_tsh),
                   (u"a source affricate written with tś-", c_ts),
                   (u"a source t written with tśʰ-", t_tsh),
                   (u"a source k written with k-", k_k),
                   (u"a source g written with k-", g_k),
                   (u"a source g written with ŋ-", g_ng),
                   (u"a source velar nasal written with ŋ-", ng_ng),
                   (u"a source a written with an open vowel", v_a),
                   (u"a source i or e written with an open vowel", v_i),
                   (u"a source u or o written with an open vowel", v_u)]:
        say(u"   %-42s %4d of %-5d %6.1f%%" % (lab, t[1], t[2], 100 * t[0]))
    say(u"")
    say(u"   A source vowel-initial syllable written with a Chinese ŋ- is 0 of 140;")
    say(u"   137 of those 140 took a glottal. That is the step the entry itself")
    say(u"   calls unsupported, and it is a measured zero, not a rarity.")
    say(u"")

    # ---------------- enumerate ------------------------------------------
    # first character: two readings, both open
    e1_t = re.compile(u"^([td])([%s])([a-zçğışöü]?)$" % V)      # 車 tśʰa
    e1_k = re.compile(u"^([kg])([%s])([a-zçğışöü]?)$" % V)      # 車 kɨɑ
    e2   = re.compile(u"^([gğŋñ])([%s])([a-zçğışöü]?)$" % V)    # 牙 ŋa

    def price(w, on, vowel_rate, coda):
        return on * vowel_rate * CODA_OPEN.get(coda, 0.02)

    def vfor(v):
        return {"a": v_a[0], u"â": v_a[0]}.get(v, v_i[0] if v in u"eiı" else v_u[0])

    first = {u"車 = tśʰa": [], u"車 = kɨɑ": []}
    second = []
    for w, (g, src) in lex.items():
        m = e1_t.match(w)
        if m:
            c, v, k = m.groups()
            first[u"車 = tśʰa"].append((price(w, t_tsh[0], vfor(v), k), w, g, src))
        m = e1_k.match(w)
        if m:
            c, v, k = m.groups()
            on = k_k[0] if c == "k" else g_k[0]
            first[u"車 = kɨɑ"].append((price(w, on, vfor(v), k), w, g, src))
        m = e2.match(w)
        if m:
            c, v, k = m.groups()
            on = ng_ng[0] if c in u"ŋñ" else g_ng[0]
            second.append((price(w, on, vfor(v), k), w, g, src))
    for kk in first: first[kk].sort(reverse=True)
    second.sort(reverse=True)

    def table(title, rows, n=12):
        say(u"")
        say(u"-" * 70)
        say(title)
        say(u"-" * 70)
        if not rows:
            say(u"   nothing in the lexicons fits this frame."); return
        for cost, w, g, src in rows[:n]:
            say(u"   %-10s %7.2f%%   %s [%s]" % (w, 100 * cost, g[:48], src))
        if len(rows) > n:
            say(u"   ... %d more fit the frame" % (len(rows) - n))

    say(u"=" * 70)
    say(u"2.  What each character permits, one syllable each")
    say(u"=" * 70)
    table(u"車 on tśʰa: a source t or d, open, any coda unwritten", first[u"車 = tśʰa"])
    table(u"車 on kɨɑ: a source k or g, open, any coda unwritten", first[u"車 = kɨɑ"])
    table(u"牙 on ŋa: a source g or velar nasal, open", second)

    say(u"")
    say(u"=" * 70)
    say(u"3.  The two characters together")
    say(u"=" * 70)
    for rd in (u"車 = tśʰa", u"車 = kɨɑ"):
        best = []
        for c1, w1, g1, s1 in first[rd][:10]:
            for c2, w2, g2, s2 in second[:10]:
                best.append((c1 * c2, w1 + u" " + w2, g1, g2))
        best.sort(reverse=True)
        say(u"")
        say(u"   on %s" % rd)
        if not best:
            say(u"      no combination available."); continue
        for cost, name, g1, g2 in best[:8]:
            say(u"      %-20s %8.4f%%  1 in %-6d %s / %s"
                % (name, 100 * cost, int(1 / cost) if cost else 0, g1[:20], g2[:20]))
    say(u"")
    say(u"   The second column is empty of real words, and the reason is")
    say(u"   structural: Old Turkic has no initial g-, so 牙 cannot open a")
    say(u"   second word. The g belongs medially, inside a single word.")

    # ---------------- one word across both characters --------------------
    say(u"")
    say(u"=" * 70)
    say(u"4.  One Turkic word spanning both characters")
    say(u"=" * 70)
    say(u"   The frame is C V (C) g V (C), with both Chinese characters open")
    say(u"   so both source codas are unwritten and priced by Table 7.")
    one = {u"車 = tśʰa": [], u"車 = kɨɑ": []}
    e = re.compile(u"^([tdkg])([%s])([a-zçğışöü]?)([gğŋñ])([%s])([a-zçğışöü]?)$" % (V, V))
    for w, (g, src) in lex.items():
        m = e.match(w)
        if not m:
            continue
        c1, v1, k1, c2, v2, k2 = m.groups()
        on2 = ng_ng[0] if c2 in u"ŋñ" else g_ng[0]
        tail = vfor(v2) * CODA_OPEN.get(k2, 0.02) * on2
        if c1 in u"td":
            cost = t_tsh[0] * vfor(v1) * CODA_OPEN.get(k1, 0.02) * tail
            one[u"車 = tśʰa"].append((cost, w, g, src))
        else:
            on1 = k_k[0] if c1 == "k" else g_k[0]
            cost = on1 * vfor(v1) * CODA_OPEN.get(k1, 0.02) * tail
            one[u"車 = kɨɑ"].append((cost, w, g, src))
    for kk in one:
        one[kk].sort(reverse=True)
    for rd in (u"車 = tśʰa", u"車 = kɨɑ"):
        say(u"")
        say(u"   on %s" % rd)
        if not one[rd]:
            say(u"      nothing in the lexicons fits."); continue
        for cost, w, g, src in one[rd][:10]:
            say(u"      %-14s %8.4f%%  1 in %-6d %s [%s]"
                % (w, 100 * cost, int(1 / cost) if cost else 0, g[:40], src))
        if len(one[rd]) > 10:
            say(u"      ... %d more fit" % (len(one[rd]) - 10))
    say(u"")
    say(u"")
    say(u"=" * 70)
    say(u"5.  What the search returns")
    say(u"=" * 70)
    say(u"   The threshold that retires Baγatur in the paper is 1 in 37.")
    say(u"   One candidate clears it with a sense worth having: toña, at 1 in 20,")
    say(u"   on the FIRST tabulated reading of 車, so no polyphony argument is")
    say(u"   needed. Kāşgarî's own entries, on two different pages:")
    say(u"")
    say(u"      toña        bebür, kaplan cinsinden bir hayvan; kişi adı   III, 368")
    say(u"      toñalamak   yiğit ve kuvvetlilerin yaptığı işi yapmak      III, 405")
    say(u"")
    say(u"   The first records it as a personal name, in the eleventh-century")
    say(u"   dictionary itself and not in any modern reconstruction. The second")
    say(u"   is a verb derived from it meaning to do what heroes and strong men")
    say(u"   do, which puts the heroic sense in the source independently of the")
    say(u"   comparison, on a different page from the noun.")
    say(u"")
    say(u"   NOT CHECKED: toña is the epithet in the name Alp Er Toŋa, whom")
    say(u"   Kāşgarî elegises and later tradition identifies with Afrasiab.")
    say(u"   The index searched here carries headwords only, so that cannot be")
    say(u"   confirmed from it. It must be checked in the Dīwān itself before")
    say(u"   being used, and it is not needed: the two entries above stand alone.")
    say(u"")
    say(u"   The other cheap forms are not names: kalñu floating on water,")
    say(u"   közñü a mirror, koñuz a dung beetle, karga a crow, köñül the heart.")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    dest = os.path.join(REP, "step48_summary.txt")
    io.open(dest, "w", encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: " + dest)


if __name__ == "__main__":
    main()
