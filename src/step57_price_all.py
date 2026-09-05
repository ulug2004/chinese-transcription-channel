# -*- coding: utf-8 -*-
r"""
Step 57.  Every row of the record priced by one method.

Until now the supplement's prices came from about eight hand-written
calculations in steps 47 to 55, each making its own choices, and sixteen
rows carried no figure at all.  This step runs price_engine over all forty
rows and produces one table.

TWO COLUMNS, because one of them is misleading on its own.  The RAW figure
is the product of the measured rates.  It falls with every extra character,
so sorting on it sorts mostly by name length: an eight-character name is
dear because it is long, not because the reading is bad.  The PER CHARACTER
figure is the geometric mean, raw**(1/characters), which is comparable
across lengths.  Both are given and either can be sorted on.

WHAT THE FLAGS MEAN.  A price is only as good as its worst cell.  Each row
carries the count of cells that were measured, assumed, or unmeasurable,
and rows blocked by a zero are listed separately with the kind of zero
named.  A zero is reported as an INVENTORY GAP when the Chinese initial is
the regular vehicle for some other source phoneme: Sanskrit then always had
an exact match available and never had to make the substitution, so the
corpus did not test it.  That is a different thing from a contested zero
and must not be read as a ban.

Output: reports\step57_prices.txt and data\derived\name_prices.csv
"""
import csv, io, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
sys.path.insert(0, HERE)
import price_engine as PE

# figures already in print, for comparison
HAND = {u"軍臣": "1 in 5", u"車牙若鞮": "1 in 20", u"當戶": "1 in 46",
        u"狐鹿姑": "1 in 52", u"烏累若鞮": "1 in 4 (element)",
        u"冒頓": u"§9.2", u"若鞮": u"§9", u"徑路": u"§9.1"}


def run(R, rows, label):
    out, failed = [], []
    for r in rows:
        zi = r["chinese"].strip(); rd = (r["proposed_name"] or "").strip()
        if not rd or rd.startswith("("):
            failed.append((zi, rd, u"no proposal" if not rd else u"compound row"))
            continue
        a, err, note = PE.price_name(zi, rd, R)
        if a is None:
            failed.append((zi, rd, err))
            continue
        out.append(dict(chinese=zi, reading=rd, price=a.price, per_char=a.per_char,
                        roles=a.roles, nchar=a.nchar, nsyl=a.nsyl,
                        flags=a.flags, note=note, detail=a.detail))
    return out, failed


def fmt(rows, key, title, say):
    say(u"")
    say(u"=" * 78)
    say(title)
    say(u"=" * 78)
    say(u"   %-10s %-20s %11s %9s %6s %-6s %s"
        % ("chinese", "reading", "1 in", "per char", "chars", "roles", "cells"))
    for d in sorted(rows, key=lambda x: x[key]):
        f = d["flags"]
        bad = sum(v for k, v in f.items() if k.startswith("assumed") or k.startswith("unmeasured"))
        cells = u"%d measured" % sum(v for k, v in f.items() if k.startswith("measured"))
        if bad:
            cells += u", %d assumed/unmeasured" % bad
        say(u"   %-10s %-20s %11s %8.1f%% %6d %-6s %s"
            % (d["chinese"], d["reading"][:20],
               "{:,}".format(int(1 / d["price"])) if d["price"] else "-",
               100 * d["per_char"], d["nchar"], d["roles"], cells))


def main():
    R = PE.Rates()
    rows = list(csv.DictReader(io.open(os.path.join(DER, "author_proposals.csv"),
                                       encoding="utf-8-sig")))
    priced, failed = run(R, rows, "current")

    lines = []
    def say(s=u""):
        try:
            print(s)
        except Exception:
            print(s.encode("ascii", "replace").decode("ascii"))
        lines.append(s)

    say(u"Step 57.  Every row of the record priced by one method.")
    say(u"Corpus: %d aligned pairs.  Rows: %d.  Priced: %d.  Not priced: %d."
        % (R.n_pairs, len(rows), len(priced), len(failed)))
    if PE.VARIANT:
        say(u"")
        say(u"   Four characters are tabulated by Schuessler only in their")
        say(u"   simplified shape and were unpriceable until now. The traditional")
        say(u"   form is mapped onto it here: %s"
            % u", ".join(u"%s=%s" % (a, b) for a, b in sorted(PE.VARIANT.items())))

    fmt(priced, "price", u"TABLE 1a.  Sorted by RAW price, dearest first", say)
    fmt(priced, "per_char", u"TABLE 1b.  Sorted PER CHARACTER, dearest first", say)

    say(u"")
    say(u"=" * 78)
    say(u"NOT PRICED")
    say(u"=" * 78)
    for zi, rd, why in failed:
        say(u"   %-12s %-22s %s" % (zi, rd[:22], why))

    say(u"")
    say(u"=" * 78)
    say(u"AGAINST THE FIGURES ALREADY IN PRINT")
    say(u"=" * 78)
    for d in priced:
        if d["chinese"] in HAND:
            say(u"   %-10s %-18s in print %-16s uniform 1 in %s"
                % (d["chinese"], d["reading"][:18], HAND[d["chinese"]],
                   "{:,}".format(int(1 / d["price"]))))

    say(u"")
    say(u"=" * 78)
    say(u"WHERE THE PRICES REST ON SOMETHING WEAKER THAN A MEASUREMENT")
    say(u"=" * 78)
    agg = collections.Counter()
    for d in priced:
        for k, v in d["flags"].items():
            agg[k] += v
    for k, v in agg.most_common():
        say(u"   %-34s %4d" % (k, v))

    dest = os.path.join(DER, "name_prices.csv")
    with io.open(dest, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["chinese", "reading", "price", "one_in", "per_char",
                    "n_chars", "n_syllables", "roles", "measured_cells",
                    "assumed_cells", "note", "alignment"])
        for d in sorted(priced, key=lambda x: x["price"]):
            f_ = d["flags"]
            w.writerow([d["chinese"], d["reading"], "%.9f" % d["price"],
                        int(1 / d["price"]), "%.5f" % d["per_char"],
                        d["nchar"], d["nsyl"], d["roles"],
                        sum(v for k, v in f_.items() if k.startswith("measured")),
                        sum(v for k, v in f_.items()
                            if k.startswith("assumed") or k.startswith("unmeasured")),
                        d["note"], d["detail"]])
        for zi, rd, why in failed:
            w.writerow([zi, rd, "", "", "", "", "", "", "", "", why, ""])
    say(u"")
    say(u"   written: data\\derived\\name_prices.csv")

    if not os.path.isdir(REP):
        os.makedirs(REP)
    io.open(os.path.join(REP, "step57_prices.txt"), "w",
            encoding="utf-8").write(u"\n".join(lines) + u"\n")
    print("")
    print("written: reports/step57_prices.txt")


if __name__ == "__main__":
    main()
