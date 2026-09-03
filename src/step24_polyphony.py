# -*- coding: utf-8 -*-
"""
step24_polyphony.py -- how many of the characters in the Xiongnu record have
more than one Later Han reading, and did we take the right one?

Schuessler's table lists a character once per reading. A character with two or
three readings gives the transcription that many possible values, and the
reconstruction column of Appendix A shows only one of them. This step counts
how often that choice was made, and whether the value we print is the first
row in the table (which is what an extractor that keeps the first hit would
produce) or a later one (which implies the choice was deliberate).

The question is not the same as reading-anchoring. A character can be
reading-anchored, meaning the channel learned an emission row for it, and still
be polyphonic, meaning the reading that row was attached to was one of several.

Input : data/derived/author_proposals.csv      (chinese, later_han)
        data/external/LHantab.tsv              (Schuessler)
Output: data/derived/polyphony.csv , reports/step24_summary.txt
"""
import csv, io, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")

def main():
    lh_path = os.path.join(EXT, "LHantab.tsv")
    ap_path = os.path.join(DER, "author_proposals.csv")
    for p in (lh_path, ap_path):
        if not os.path.exists(p): sys.exit("Missing: %s" % p)

    # character -> list of readings, in table order
    LH = collections.OrderedDict()
    with io.open(lh_path, encoding="utf8", errors="ignore") as f:
        for x in csv.DictReader(f, delimiter="\t"):
            z = (x.get("zi") or "").strip()
            if not z: continue
            syl = (x.get("syl_bok") or "").strip()
            if not syl:
                syl = (x.get("con") or "") + (x.get("vow") or "") + (x.get("ton") or "")
            LH.setdefault(z, [])
            if syl not in LH[z]: LH[z].append(syl)
    print("Later Han table: %d distinct characters" % len(LH))

    with io.open(ap_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    out, n = [], collections.Counter()
    unaligned = []
    for r in rows:
        zi   = (r.get("chinese") or "").strip()
        read = (r.get("later_han") or "").split()
        if not zi: continue
        n["items"] += 1
        if len(read) != len(zi):
            unaligned.append((zi, r.get("later_han") or ""))
            n["items_unaligned"] += 1
            continue
        item_poly = 0
        for ch, used in zip(zi, read):
            alts = LH.get(ch)
            n["characters"] += 1
            if not alts:
                n["char_not_in_table"] += 1
                out.append({"item": zi, "character": ch, "reading_used": used,
                            "n_readings": 0, "position_used": "",
                            "alternatives": ""}); continue
            k = len(alts)
            n["char_single" if k == 1 else "char_polyphonic"] += 1
            if k > 1: item_poly += 1
            pos = (alts.index(used) + 1) if used in alts else 0
            if k > 1:
                n["used_is_first" if pos == 1 else
                  ("used_not_in_table" if pos == 0 else "used_is_later_row")] += 1
            out.append({"item": zi, "character": ch, "reading_used": used,
                        "n_readings": k, "position_used": pos,
                        "alternatives": " | ".join(a for a in alts if a != used)})
        if item_poly: n["items_with_polyphony"] += 1
        n["poly_chars_in_items"] += item_poly

    c = n["char_polyphonic"] + n["char_single"]
    pct = (100.0 * n["char_polyphonic"] / c) if c else 0.0
    L = []
    A = L.append
    A("step 24 - polyphonic characters in the Xiongnu record")
    A("")
    A("Items examined                                  : %d" % n["items"])
    if n["items_unaligned"]:
        A("  skipped, reading does not align to characters : %d" % n["items_unaligned"])
    A("Characters examined                             : %d" % c)
    A("  one reading in Schuessler's table             : %d" % n["char_single"])
    A("  more than one reading                         : %d  (%.0f%%)" % (n["char_polyphonic"], pct))
    if n["char_not_in_table"]:
        A("  not in the table at all                       : %d" % n["char_not_in_table"])
    A("")
    A("Items containing at least one polyphonic character: %d of %d" % (n["items_with_polyphony"], n["items"]))
    A("")
    A("Where a character has several readings, the value printed in Appendix A is")
    A("  the FIRST row of the table  : %d" % n["used_is_first"])
    A("  a LATER row                 : %d" % n["used_is_later_row"])
    A("  not in the table at all     : %d" % n["used_not_in_table"])
    A("")
    A("Reading: a high 'first row' count is what an extractor that keeps the first")
    A("hit per character produces, and does not by itself show that the reading was")
    A("chosen. Characters listed in polyphony.csv with n_readings > 1 are the ones")
    A("where the transcription permits a value other than the one we print.")
    A("")
    A("This is not the same as reading-anchoring (S1.5). A character can be anchored")
    A("in the channel and still be polyphonic here.")
    A("")
    if unaligned:
        A("Items skipped because the reading string did not align character by character:")
        for zi, rd in unaligned: A("  %s   %s" % (zi, rd))
        A("")
    A("Polyphonic characters, with the alternatives not used:")
    seen = set()
    for d in out:
        if d["n_readings"] > 1 and d["character"] not in seen:
            seen.add(d["character"])
            A("  %s  used %-10s (row %s of %d)   also: %s"
              % (d["character"], d["reading_used"], d["position_used"],
                 d["n_readings"], d["alternatives"]))

    txt = "\n".join(L)
    print(); print(txt)

    if not os.path.isdir(REP): os.makedirs(REP)
    with io.open(os.path.join(DER, "polyphony.csv"), "w",
                 encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["item", "character", "reading_used",
                                          "n_readings", "position_used", "alternatives"])
        w.writeheader(); w.writerows(out)
    with io.open(os.path.join(REP, "step24_summary.txt"), "w", encoding="utf8") as f:
        f.write(txt + "\n")
    print("\nWrote data/derived/polyphony.csv and reports/step24_summary.txt")

if __name__ == "__main__":
    main()
