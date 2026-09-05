# -*- coding: utf-8 -*-
r"""
Step 58.  The corpus repaired, and every price recomputed on it.

Step 56 established the defect: the 1,017 verified Sanskrit pairs contain
no two-character transcription at all, while 21 of the record's 40 items
are two-character names.  The missing entries were parked as "ambiguous"
not for their sound, which scores 1.00, but because a two-character Chinese
string is often an ordinary word and the labeller could not separate a
transcription from a calque by shape.

The exclusion is not random.  It is systematically the shortest forms, and
a scribe writing a two-syllable word in two characters has no slack: no
spare character, no room to compress.  So the rates may be biased by
length, not merely imprecise, and biased in the direction that matters,
since more than half the record is two-character names.

THIS STEP REPAIRS THE CORPUS AND MEASURES WHAT THE REPAIR CHANGES.  The
promoted pairs carry a provenance column so the corpus can be regenerated
with or without them, and the sensitivity is reported rather than hidden:
if the deltas are small that is evidence the results are robust to a known
defect, and if a reading changes rank we needed to know.

Outputs
  data\derived\nti_transcription_pairs_v2.csv
  data\derived\name_prices_v2.csv
  reports\step58_summary.txt
"""
import csv, io, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import price_engine as PE
import step56_two_character as S56
import step57_price_all as S57


def promoted():
    INI = S56.initials()
    amb = S56.load("nti_ambiguous.csv")
    _t, _p, hits = S56.sweep(amb, INI, 2)
    keep = [r for r in hits
            if ((r.get("trad") or "").strip(), (r.get("skt") or "").strip())
            not in S56.HAND_REJECT]
    for r in keep:
        r["align"] = "exact"
        r["label"] = "transcription"
        r["provenance"] = "promoted by step 56 from nti_ambiguous.csv"
    return keep


def write_v2(keep):
    base = list(csv.DictReader(io.open(os.path.join(DER, "nti_transcription_pairs.csv"),
                                       encoding="utf-8-sig")))
    cols = list(base[0].keys()) + ["provenance"]
    dest = os.path.join(DER, "nti_transcription_pairs_v2.csv")
    with io.open(dest, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(cols)
        for r in base:
            w.writerow([r.get(c, "") for c in cols[:-1]] + ["original 1,017"])
        for r in keep:
            w.writerow([r.get(c, "") for c in cols[:-1]] + [r["provenance"]])
    return dest, len(base) + len(keep)


def rate_table(R):
    """The headline rates the paper quotes, so the delta can be reported."""
    out = collections.OrderedDict()
    def o(srcs, ci):
        a = sum(R.o_cell[(s, ci)] for s in srcs); b = sum(R.o_tot[s] for s in srcs)
        return (a, b, float(a) / b if b else 0.0)
    def v(k, cl):
        return (R.v_cell[(k, cl)], R.v_tot[k],
                float(R.v_cell[(k, cl)]) / R.v_tot[k] if R.v_tot[k] else 0.0)
    out[u"source k written with a Chinese k-"] = o(["k"], u"k")
    out[u"source g written with a Chinese g-"] = o(["g", "gh"], u"g")
    out[u"source l written with a Chinese l-"] = o(["l"], u"l")
    out[u"source m written with a Chinese m-"] = o(["m"], u"m")
    out[u"source c written with a Chinese dź-"] = o(["c"], u"dź")
    out[u"source c written with a Chinese tś-"] = o(["c"], u"tś")
    out[u"source t written with a Chinese tśʰ-"] = o(["t"], u"tśʰ")
    out[u"source ś written with a Chinese ś-"] = o([u"ś"], u"ś")
    out[u"source i or e on a front vowel"] = v("i/e", "front")
    out[u"source u or o on a rounded vowel"] = v("u/o", "rounded")
    out[u"source a on an open vowel"] = v("a", "open")
    t = sum(R.vi.values())
    out[u"a vowel-initial syllable on a glottal"] = (R.vi.get(u"ʔ", 0), t,
                                                    float(R.vi.get(u"ʔ", 0)) / t if t else 0)
    out[u"a vowel-initial syllable on a velar"] = (R.vi.get(u"k", 0), t, 0.0)
    return out


def main():
    lines = []
    def say(s=u""):
        try:
            print(s)
        except Exception:
            print(s.encode("ascii", "replace").decode("ascii"))
        lines.append(s)

    keep = promoted()
    dest, total = write_v2(keep)

    R1 = PE.Rates()
    R2 = PE.Rates(extra_pairs=keep)

    say(u"Step 58.  The corpus repaired, and every price recomputed on it.")
    say(u"")
    say(u"   pairs before                    %5d" % 1017)
    say(u"   promoted from the parked pool   %5d" % len(keep))
    say(u"   pairs after                     %5d" % total)
    say(u"   aligned one-to-one before       %5d" % R1.n_pairs)
    say(u"   aligned one-to-one after        %5d" % R2.n_pairs)
    say(u"   written: data\\derived\\nti_transcription_pairs_v2.csv")
    say(u"")

    say(u"=" * 78)
    say(u"THE HEADLINE RATES, BEFORE AND AFTER")
    say(u"=" * 78)
    a, b = rate_table(R1), rate_table(R2)
    say(u"   %-42s %-16s %-16s %s" % ("", "before", "after", "delta"))
    moved = []
    for k in a:
        n1, d1, p1 = a[k]; n2, d2, p2 = b[k]
        dd = 100 * (p2 - p1)
        say(u"   %-42s %4d/%-5d %5.1f%%  %4d/%-5d %5.1f%%  %+5.1f pts"
            % (k, n1, d1, 100 * p1, n2, d2, 100 * p2, dd))
        if abs(dd) >= 1.0:
            moved.append((k, 100 * p1, 100 * p2, dd))
    say(u"")
    if moved:
        say(u"   Rates that moved by a point or more:")
        for k, x, y, d in sorted(moved, key=lambda z: -abs(z[3])):
            say(u"       %-40s %.1f%% -> %.1f%%  (%+.1f)" % (k, x, y, d))
    else:
        say(u"   No headline rate moved by as much as one point.")
    say(u"")

    rows = list(csv.DictReader(io.open(os.path.join(DER, "author_proposals.csv"),
                                       encoding="utf-8-sig")))
    p1, f1 = S57.run(R1, rows, "before")
    p2, f2 = S57.run(R2, rows, "after")
    S57.fmt(p2, "price", u"TABLE 2a.  On the repaired corpus, RAW price, dearest first", say)
    S57.fmt(p2, "per_char", u"TABLE 2b.  On the repaired corpus, PER CHARACTER, dearest first", say)

    say(u"")
    say(u"=" * 78)
    say(u"WHAT THE REPAIR DID TO EACH NAME")
    say(u"=" * 78)
    m1 = {d["chinese"]: d for d in p1}
    m2 = {d["chinese"]: d for d in p2}
    r1 = {c: i for i, c in enumerate(sorted(m1, key=lambda c: m1[c]["price"]))}
    r2 = {c: i for i, c in enumerate(sorted(m2, key=lambda c: m2[c]["price"]))}
    say(u"   %-10s %-18s %12s %12s %9s %s"
        % ("chinese", "reading", "1 in before", "1 in after", "change", "rank"))
    big = []
    for c in sorted(m2, key=lambda c: m2[c]["price"]):
        d2 = m2[c]
        if c not in m1:
            say(u"   %-10s %-18s %12s %12s %9s %s"
                % (c, d2["reading"][:18], "not priced",
                   "{:,}".format(int(1 / d2["price"])), "NEW", ""))
            continue
        d1 = m1[c]
        ch = d2["price"] / d1["price"] - 1.0
        rk = r2[c] - r1[c]
        say(u"   %-10s %-18s %12s %12s %8.1f%% %s"
            % (c, d2["reading"][:18], "{:,}".format(int(1 / d1["price"])),
               "{:,}".format(int(1 / d2["price"])), 100 * ch,
               (u"%+d" % rk) if rk else u""))
        if abs(ch) > 0.10 or rk:
            big.append((c, d2["reading"], 100 * ch, rk))
    say(u"")
    say(u"   rows newly priceable: %d" % len([c for c in m2 if c not in m1]))
    say(u"   rows that moved more than 10%% or changed rank: %d" % len(big))
    for c, rd, ch, rk in big:
        say(u"       %-10s %-18s %+.1f%%  rank %+d" % (c, rd[:18], ch, rk))
    say(u"")
    say(u"=" * 78)
    say(u"THRESHOLDS THE PAPER USES")
    say(u"=" * 78)
    say(u"   1 in 37 retires Baγatur in §8.1. Rows dearer than that:")
    for c in sorted(m2, key=lambda c: m2[c]["price"]):
        if m2[c]["price"] < 1 / 37.0:
            was = (u"was 1 in %s" % "{:,}".format(int(1 / m1[c]["price"]))) if c in m1 else u"new"
            say(u"       %-10s %-18s 1 in %-10s %s"
                % (c, m2[c]["reading"][:18], "{:,}".format(int(1 / m2[c]["price"])), was))

    with io.open(os.path.join(DER, "name_prices_v2.csv"), "w",
                 encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["chinese", "reading", "one_in_before", "one_in_after",
                    "per_char_after", "n_chars", "roles", "note"])
        for c in sorted(m2, key=lambda c: m2[c]["price"]):
            w.writerow([c, m2[c]["reading"],
                        int(1 / m1[c]["price"]) if c in m1 else "",
                        int(1 / m2[c]["price"]), "%.5f" % m2[c]["per_char"],
                        m2[c]["nchar"], m2[c]["roles"], m2[c]["note"]])
        for zi, rd, why in f2:
            w.writerow([zi, rd, "", "", "", "", "", why])

    if not os.path.isdir(REP):
        os.makedirs(REP)
    io.open(os.path.join(REP, "step58_summary.txt"), "w",
            encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: reports/step58_summary.txt")


if __name__ == "__main__":
    main()
