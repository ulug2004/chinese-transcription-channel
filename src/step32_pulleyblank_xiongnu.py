# -*- coding: utf-8 -*-
"""
step32_pulleyblank_xiongnu.py -- collect every place where Pulleyblank's Lexicon
assigns a reading to a character *in a Xiongnu word*, and set those against the
readings Appendix A of the paper prints.

Why. Step 24 found that 46 of the 107 characters in the record carry more than
one Later Han reading and that we print the first tabulated row in all 46. Step
30 then found that Pulleyblank's Lexicon does not leave that choice open: it
names the Xiongnu context and assigns a reading, character by character. Three
spot checks all disagreed with the row we print:

    頓  we print tuənᶜ   Pulleyblank: the reading du, for Modun
    谷  we print kok     Pulleyblank: lu, "luli king, Xiongnu title"  (K1202a)
    閼  we print ʔɑt     Pulleyblank: yan, EMC ʔen, for yanzhi         (K270a)

Doing this row by row is how the 谷蠡 entry came to be written on a reading the
Lexicon rules out. This step collects all of them in one pass instead.

The Lexicon's Chinese does not encode (OCR without CJK), so the search is on
the romanisation and on the words that mark a Xiongnu context. Entries look like

    lu 150:0 M36182C  Y. [lu] L. luwk E. lawk
    K1202a luli king Xiongnu title. See also gu, yu

so a hit on the gloss line needs the line above it to get the readings, and the
script keeps a window either side.

Input : new_refs\\ or References\\  Pulleyblank 1991 PDF
        data/derived/author_proposals.csv   (for the pinyin of each item)
Output: reports\\step32_summary.txt
        reports\\readings\\pulleyblank_xiongnu_blocks.txt
        data/derived/pulleyblank_xiongnu.csv
"""
import csv, io, os, re, sys, glob, collections, logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
OUT  = os.path.join(REP, "readings")
DIRS = [os.path.join(ROOT, d) for d in ("References", "new_refs", "my_resources")]

# distinctive strings: safe as plain substrings
LONG = ["xiongnu", "hsiung-nu", "hiung-nu", "xiong-nu", "shanyu", "shan-yu",
        "shan-yü", "chanyu", "yanzhi", "yanzhl", "luli", "lull", "juqu",
        "modun", "mao-tun", "maodun", "tuqi", "ruodi", "chengli", "gutu",
        "danghu", "gudu", "jinglu", "funi", "outuo", "hulu", "xulianti",
        "luandi", "touman", "jizhou", "junchen", "chengli", "guli"]
# short and ambiguous: word-boundary only
SHORT = [r"\bhun\b", r"\bhuns\b", r"\bjie\b", r"\bhu\b"]

def find_pdf():
    for d in DIRS:
        if not os.path.isdir(d): continue
        for p in glob.glob(os.path.join(d, "**", "*.pdf"), recursive=True):
            if "lexicon of reconstructed" in os.path.basename(p).lower():
                return p
    return None

READING = re.compile(r"\bE\.\s*([^\s].{0,24})$")
KNUM    = re.compile(r"\bK\s?(\d{2,4}[a-z]?)\b")

def main():
    p = find_pdf()
    if not p: sys.exit("Pulleyblank 1991 PDF not found.")
    for d in (OUT, DER):
        if not os.path.isdir(d): os.makedirs(d)
    import pdfplumber
    print("  %s" % os.path.basename(p)[:60])

    shorts = [re.compile(r) for r in SHORT]
    blocks, rows = [], []
    tally = collections.Counter()
    n = 0
    with pdfplumber.open(p) as pdf:
        for pg in pdf.pages:
            n += 1
            if n % 50 == 0:
                sys.stdout.write("   page %d\r" % n); sys.stdout.flush()
            t = pg.extract_text() or ""
            if not t: continue
            lines = t.splitlines()
            for j, line in enumerate(lines):
                ll = line.lower()
                hit = None
                for k in LONG:
                    if k in ll: hit = k; break
                if not hit:
                    for rx in shorts:
                        if rx.search(ll): hit = rx.pattern; break
                if not hit: continue
                tally[hit] += 1
                lo = max(0, j-3); hi = min(len(lines), j+3)
                blk = "\n".join(lines[lo:hi])
                blocks.append((n, hit, blk))
                # try to pull the pinyin, the K number and the EMC out of the window
                py = ""
                for l in lines[lo:hi]:
                    m = re.match(r"\s*([a-zàáâäèéêìíîòóôöùúûü']{1,10})\s+\d", l)
                    if m: py = m.group(1); break
                kn = ""
                m = KNUM.search(blk)
                if m: kn = "K" + m.group(1)
                emc = ""
                for l in lines[lo:hi]:
                    m = READING.search(l)
                    if m: emc = m.group(1).strip(); break
                rows.append({"pdf_page": n, "matched": hit, "pinyin": py,
                             "k_number": kn, "emc_guess": emc,
                             "block": blk.replace("\n", " | ")})
    print("   pages: %d   blocks: %d" % (n, len(blocks)))

    # which of the 40 items do these touch?
    ap = os.path.join(DER, "author_proposals.csv")
    touched = collections.defaultdict(set)
    if os.path.exists(ap):
        with io.open(ap, encoding="utf-8-sig") as f:
            items = [(r["chinese"], (r.get("pinyin") or "").lower()) for r in csv.DictReader(f)]
        allblocks = " ".join(b.lower() for _, _, b in blocks)
        for zh, py in items:
            if py and py in allblocks: touched[zh].add("pinyin of the whole item")
            for syl in re.findall(r"[a-z]+", py):
                if len(syl) > 2 and re.search(r"\b" + syl + r"\b", allblocks):
                    touched[zh].add(syl)

    L=[]; A=L.append
    A("step 32 - Pulleyblank's Lexicon on the Xiongnu words")
    A("")
    A("Entry blocks naming a Xiongnu context: %d" % len(blocks))
    A("")
    A("What matched, and how often:")
    for k, v in tally.most_common():
        A("   %-14s %d" % (k, v))
    A("")
    A("A keyword with a very high count is probably matching inside other words;")
    A("check it in the blocks file before trusting it.")
    A("")
    A("Items of the record these blocks appear to touch: %d of 40" % len(touched))
    for zh in sorted(touched):
        A("   %-14s via %s" % (zh, ", ".join(sorted(touched[zh]))))
    A("")
    A("Next: for each item above, compare Pulleyblank's assigned reading with the")
    A("value Appendix A prints. Where they differ, the paper is printing the first")
    A("row of Schuessler's table against an explicit assignment in the Lexicon.")
    txt = "\n".join(L)
    print(); print(txt)

    with io.open(os.path.join(OUT, "pulleyblank_xiongnu_blocks.txt"), "w", encoding="utf8") as f:
        f.write("Pulleyblank 1991, entry blocks naming a Xiongnu context.\n"
                "Source: %s\nOCR note: the Chinese does not encode; Y. is Early Mandarin,\n"
                "L. Late Middle Chinese, E. Early Middle Chinese.\n\n" % os.path.basename(p))
        for pno, hit, blk in blocks:
            f.write("--- p%d  [%s] ---\n%s\n\n" % (pno, hit, blk))
    with io.open(os.path.join(DER, "pulleyblank_xiongnu.csv"), "w",
                 encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["pdf_page","matched","pinyin","k_number","emc_guess","block"])
        w.writeheader(); w.writerows(rows)
    with io.open(os.path.join(REP, "step32_summary.txt"), "w", encoding="utf8") as f:
        f.write(txt + "\n")
    print("\nWrote reports\\step32_summary.txt, reports\\readings\\pulleyblank_xiongnu_blocks.txt")
    print("and data\\derived\\pulleyblank_xiongnu.csv")

if __name__ == "__main__":
    main()
