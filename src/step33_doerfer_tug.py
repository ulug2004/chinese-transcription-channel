# -*- coding: utf-8 -*-
"""
step33_doerfer_tug.py -- find Doerfer's entry 969 on tuğ across all four volumes
of Türkische und Mongolische Elemente im Neupersischen, and report which way he
takes the word to have travelled.

Why. On Pulleyblank's reading of 冒頓 the second character is du < EMC dawk, a
written velar coda, so a source tuğ "horsehair standard" would have its -ğ
written rather than unwritten: a tighter fit than any other candidate. But
Clauson marks tu:ğ F for foreign and calls it "no doubt" a loan from Chinese
*dok 纛 "banner, standard", citing Doerfer II 969. Nişanyan argues the reverse,
since the horsehair standard is a steppe artifact in continuous use. If the word
is a Chinese loan the reading is circular; if it is Turkic there is no objection
at all. Doerfer's subject is loan direction, so his entry decides it.

The set divides by the Arabic alphabet, and tuğ is توغ, beginning with tā:

    Band I   (1963)  Mongolische Elemente
    Band II  (1965)  Türkische Elemente, alif bis tā   <- entry 969 is here
    Band III (1967)  Türkische Elemente, ǰīm bis kāf
    Band IV  (1975)  Türkische Elemente (Schluss) und Register zur Gesamtarbeit

The filenames do not say which volume is which, so this script searches every
Doerfer PDF it finds, reports each one's entry-number range so the volumes can
be identified, and says which file contains 969.

Three passes per volume, because each fails differently:
  1. the headword, matched by pattern, since OCR mangles the diacritics
  2. the German gloss alone, since entry headwords begin in Arabic script and
     the Arabic comes through as noise
  3. the entry number 969 itself, with its surrounding lines

Output: reports\\readings\\doerfer_<file>_tug.txt  per volume
        reports\\readings\\doerfer_entry_969.txt   the entry, if found
        reports\\step33_summary.txt
"""
import io, os, re, sys, glob, collections, logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
OUT  = os.path.join(ROOT, "reports", "readings")
REP  = os.path.join(ROOT, "reports")
DIRS = [os.path.join(ROOT, d) for d in ("References", "new_refs", "my_resources")]

HEAD  = re.compile(r"\bt[uūùûüȗ][ġgqğǧγ]\b", re.I)
GLOSS = ["rossschweif", "roßschweif", "rosschweif", "pferdeschwanz",
         "pferdeschweif", "yakschwanz", "roßschweifbanner", "roßschweifstange"]
DIRW  = ["chin.", "chinesisch", "lehnwort", "entlehnt", "entlehnung",
         "urspr.", "ursprünglich", "mo.", "mong.", "tu.", "türk.", "herkunft"]
E969  = re.compile(r"(?m)^\s*969\s*[\.\)]")
ENTRY = re.compile(r"(?m)^\s*(\d{3,4})\s*[\.\)]\s")

def find_pdfs():
    out = []
    for d in DIRS:
        if not os.path.isdir(d): continue
        for p in glob.glob(os.path.join(d, "**", "*.pdf"), recursive=True):
            b = os.path.basename(p).lower()
            if "neupersischen" in b: out.append(p)
    return sorted(set(out))

def short(p):
    b = os.path.basename(p)
    return re.sub(r"[^A-Za-z0-9]+", "_", b)[:48]

def main():
    pdfs = find_pdfs()
    if not pdfs: sys.exit("No Doerfer (Neupersischen) PDF found.")
    for d in (OUT, REP):
        if not os.path.isdir(d): os.makedirs(d)
    import pdfplumber
    print("  Doerfer volumes found: %d" % len(pdfs))

    L=[]; A=L.append
    A("step 33 - Doerfer on tug, across all volumes")
    A("")
    found_969 = []
    for p in pdfs:
        print()
        print("  " + os.path.basename(p)[:70])
        pages=0; chars=0; nums=[]
        head_hits=[]; gloss_hits=[]; e969=[]
        with pdfplumber.open(p) as pdf:
            for pg in pdf.pages:
                pages += 1
                if pages % 25 == 0:
                    sys.stdout.write("     page %d\r" % pages); sys.stdout.flush()
                t = pg.extract_text() or ""
                chars += len(t)
                if not t: continue
                for m in ENTRY.finditer(t):
                    v = int(m.group(1))
                    if 1 <= v <= 2000: nums.append(v)
                lines = t.splitlines()
                for j, line in enumerate(lines):
                    low = line.lower()
                    blk = lambda a,b: "\n".join(lines[max(0,j-a):min(len(lines),j+b)])
                    if HEAD.search(line):       head_hits.append((pages, blk(4,8)))
                    if any(k in low for k in GLOSS): gloss_hits.append((pages, blk(6,10)))
                if E969.search(t):
                    e969.append((pages, t))
        rng = ("%d to %d, %d entries" % (min(nums), max(nums), len(set(nums)))) if nums else "none found"
        has = 969 in nums
        print("     pages %d, text %d chars, entry numbers %s" % (pages, chars, rng))
        print("     headword hits %d, gloss hits %d, entry-969 pages %d, 969 in range: %s"
              % (len(head_hits), len(gloss_hits), len(e969), has))
        A("%s" % os.path.basename(p)[:70])
        A("   pages %d, text %d characters" % (pages, chars))
        A("   entry numbers: %s" % rng)
        A("   headword hits %d, gloss hits %d, entry-969 pages %d, 969 among entries: %s"
          % (len(head_hits), len(gloss_hits), len(e969), has))
        if chars < 3000:
            A("   [!] no usable text layer; this volume is a scan and needs OCR")
        A("")
        with io.open(os.path.join(OUT, "doerfer_%s_tug.txt" % short(p)), "w", encoding="utf8") as f:
            f.write("Source: %s\nentry numbers: %s\n\n" % (os.path.basename(p), rng))
            f.write("=== headword hits ===\n\n")
            for pno, b in head_hits: f.write("--- pdf page %d ---\n%s\n\n" % (pno, b))
            f.write("\n=== horsehair-banner gloss hits ===\n\n")
            for pno, b in gloss_hits: f.write("--- pdf page %d ---\n%s\n\n" % (pno, b))
        if e969:
            found_969.append((p, e969))
    if found_969:
        with io.open(os.path.join(OUT, "doerfer_entry_969.txt"), "w", encoding="utf8") as f:
            for p, pages in found_969:
                f.write("############ %s ############\n\n" % os.path.basename(p))
                for pno, t in pages:
                    f.write("--- pdf page %d ---\n%s\n\n" % (pno, t))
        A("Entry 969 appears on a page in: %s" % ", ".join(os.path.basename(x)[:40] for x,_ in found_969))
        A("See reports\\readings\\doerfer_entry_969.txt")
        print()
        print("  *** entry 969 found. See reports\\readings\\doerfer_entry_969.txt ***")
    else:
        A("No page carried a line beginning '969.' in any volume. Either the")
        A("volume containing it has no text layer, or the OCR lost the heading.")
        print()
        print("  entry 969 not located by heading. Check the volume whose entry")
        print("  range contains 969, by eye.")
    txt="\n".join(L)
    with io.open(os.path.join(REP, "step33_summary.txt"), "w", encoding="utf8") as f:
        f.write(txt+"\n")
    print()
    print(txt)

if __name__ == "__main__":
    main()
