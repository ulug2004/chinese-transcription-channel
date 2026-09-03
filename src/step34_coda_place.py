# -*- coding: utf-8 -*-
"""
step34_coda_place.py -- when a source syllable ends in a stop, does the Chinese
coda match its place of articulation, or can it switch?

Table 7 of the paper answers a different question: how often a stop-final source
syllable was written with an OPEN character (30%). It says nothing about the
cases where a coda WAS written, and whether that coda had to be the same place.

The 冒頓 table needs this. On Schuessler's tuət the reading Bögü Tuğ would need
a source velar -ğ written by a dental -t. Whether that ever happens has never
been counted.

Method. Aligned pairs where one character corresponds to one source syllable,
so positions match. The source syllable's coda is taken as the first consonant
of a cluster of two or more between vowels; a single intervocalic consonant is
the onset of the next syllable and leaves the preceding syllable open. That is
the same syllabification heuristic step 23 uses, and it is a heuristic.

Input : data/derived/nti_transcription_pairs.csv , data/external/LHantab.tsv
Output: data/derived/coda_place.csv , reports/step34_summary.txt
"""
import csv, io, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
EXT  = os.path.join(ROOT, "data", "external")
REP  = os.path.join(ROOT, "reports")

VOWELS   = ["ai","au","ā","ī","ū","ṝ","ṛ","ḷ","a","i","u","e","o"]
DIGRAPHS = ["kh","gh","ch","jh","ṭh","ḍh","th","dh","ph","bh"]

# place of articulation of a source stop coda
PLACE = {}
for c in ("k","kh","g","gh"):   PLACE[c] = "velar"
for c in ("t","th","d","dh","ṭ","ṭh","ḍ","ḍh"): PLACE[c] = "dental"
for c in ("p","ph","b","bh"):   PLACE[c] = "labial"
# source nasal codas, kept separate: a nasal written by a stop is the step
# Bögü Tın would need on Schuessler's tuət
NASAL = {"m":"labial nasal","n":"dental nasal","ṇ":"dental nasal",
         "ñ":"palatal nasal","ṅ":"velar nasal","ṃ":"nasal (anusvara)"}
CTYPE = {"k":"velar stop","t":"dental stop","p":"labial stop",
         "ŋ":"velar nasal","n":"dental nasal","m":"labial nasal"}
# place of a Chinese coda
CPLACE = {"k":"velar","ŋ":"velar","t":"dental","n":"dental","p":"labial","m":"labial"}

def toks(s):
    s=s.lower(); out=[]; i=0
    while i < len(s):
        for v in VOWELS:
            if s.startswith(v,i): out.append(("V",v)); i+=len(v); break
        else:
            for d in DIGRAPHS:
                if s.startswith(d,i): out.append(("C",d)); i+=len(d); break
            else:
                out.append(("C",s[i])); i+=1
    return out

def codas(s):
    """coda of each source syllable: first consonant of a 2+ cluster, else None"""
    t=toks(s); out=[]; cur=[]; seen=False
    for kind,ch in t:
        if kind=="V":
            if seen: out.append(cur[0] if len(cur)>=2 else None)
            cur=[]; seen=True
        else:
            if seen: cur.append(ch)
    if seen: out.append(cur[0] if len(cur)>=2 else None)
    return out

def main():
    lh=os.path.join(EXT,"LHantab.tsv"); pr=os.path.join(DER,"nti_transcription_pairs.csv")
    for p in (lh,pr):
        if not os.path.exists(p): sys.exit("Missing: %s" % p)
    CODA={}
    with io.open(lh,encoding="utf8",errors="ignore") as f:
        for x in csv.DictReader(f,delimiter="\t"):
            z=(x.get("zi") or "").strip()
            if z and z not in CODA:
                v=(x.get("vow") or "")
                CODA[z]= v[-1:] if v[-1:] in "ptkmnŋ" else ""
    with io.open(pr,encoding="utf-8-sig") as f:
        rows=[r for r in csv.DictReader(f)
              if r.get("align")=="exact" and r.get("n_chars")==r.get("n_syl")]
    print("pairs with one character to one source syllable: %d" % len(rows))

    n=collections.Counter(); cross=collections.Counter(); nas=collections.Counter(); out=[]
    for r in rows:
        zi=(r.get("trad") or "").strip(); src=(r.get("skt") or "").strip()
        if not zi or not src: continue
        cd=codas(src)
        if len(cd)!=len(zi): continue
        for ch,sc in zip(zi,cd):
            if sc is None: continue
            if sc in NASAL:
                cc2=CODA.get(ch)
                if cc2 is None: continue
                n["nasal-final source syllables"]+=1
                t2 = "open" if cc2=="" else CTYPE.get(cc2,"other")
                nas[(NASAL[sc],t2)]+=1
                n["nasal written as a STOP" if t2.endswith("stop")
                  else ("nasal written open" if t2=="open" else "nasal written as a nasal")]+=1
                continue
            sp=PLACE.get(sc)
            if not sp: continue                       # liquid, sibilant coda: not this step
            cc=CODA.get(ch)
            if cc is None: continue
            n["stop-final source syllables"]+=1
            if cc=="":
                cross[(sp,"open")]+=1; n["written open"]+=1
            else:
                ct=CTYPE.get(cc,"other")          # e.g. "dental stop", "velar nasal"
                cross[(sp,ct)]+=1
                cp=CPLACE.get(cc,"other")
                n["same place" if cp==sp else "DIFFERENT place"]+=1
                n["stop written as a NASAL" if ct.endswith("nasal") else "stop written as a stop"]+=1
            out.append({"chinese":zi,"source":src,"character":ch,
                        "source_coda":sc,"source_place":sp,
                        "chinese_coda":cc or "(open)",
                        "chinese_place":CPLACE.get(cc,"open" if cc=="" else "other")})
    tot=n["stop-final source syllables"] or 1
    L=[];A=L.append
    A("step 34 - does a written coda have to match the source coda's place?")
    A("")
    A("Stop-final source syllables at a matched position: %d" % n["stop-final source syllables"])
    A("  written with an open character      : %4d  (%.0f%%)" % (n["written open"],100.0*n["written open"]/tot))
    A("  written with a coda of the SAME place: %4d  (%.0f%%)" % (n["same place"],100.0*n["same place"]/tot))
    A("  written with a coda of a DIFFERENT place: %4d  (%.0f%%)" % (n["DIFFERENT place"],100.0*n["DIFFERENT place"]/tot))
    A("")
    A("Cross-tabulation, source place by Chinese place:")
    A("")
    places=["velar","dental","labial"]
    cols=["open","velar stop","dental stop","labial stop",
          "velar nasal","dental nasal","labial nasal"]
    A("  source stop coda \\ Chinese coda")
    A("  %-16s %5s %6s %7s %7s %7s %7s %7s" % ("", "open","vel-k","den-t","lab-p","vel-ng","den-n","lab-m"))
    for sp in places:
        row=[cross[(sp,c)] for c in cols]
        A("  %-16s %5d %6d %7d %7d %7d %7d %7d" % (sp,*row))
    A("")
    A("  of the written cases: same place %d, different place %d" % (n["same place"],n["DIFFERENT place"]))
    A("  stop written as a stop %d, stop written as a NASAL %d"
      % (n["stop written as a stop"],n["stop written as a NASAL"]))
    A("")
    A("Reading: the diagonal is the same-place cases. Anything off the diagonal and")
    A("not in the open column is a coda that switched place. That is the step the")
    A("Bögü Tuğ reading of 冒頓 would need on Schuessler's tuət, where a source")
    A("velar would have to be written by a dental -t.")
    A("")
    tn=n["nasal-final source syllables"] or 1
    A("")
    A("Source NASAL codas, kept separate: %d" % n["nasal-final source syllables"])
    A("  written as a nasal   : %4d  (%.0f%%)" % (n["nasal written as a nasal"],100.0*n["nasal written as a nasal"]/tn))
    A("  written open         : %4d  (%.0f%%)" % (n["nasal written open"],100.0*n["nasal written open"]/tn))
    A("  written as a STOP    : %4d  (%.0f%%)" % (n["nasal written as a STOP"],100.0*n["nasal written as a STOP"]/tn))
    A("")
    A("  detail:")
    for k,v in sorted(nas.items(), key=lambda x:-x[1]):
        A("    %-18s -> %-14s %4d" % (k[0],k[1],v))
    A("")
    A("The last figure is the step Bögü Tın would need on Schuessler's tuət: a")
    A("source -n written by a dental STOP coda rather than a nasal one.")
    A("")
    A("Caveat: the source coda is assigned by the same syllabification heuristic")
    A("step 23 uses, and the whole count is on the one-to-one aligned subset, so")
    A("compressed spellings are excluded by construction.")
    txt="\n".join(L); print(); print(txt)
    if not os.path.isdir(REP): os.makedirs(REP)
    with io.open(os.path.join(DER,"coda_place.csv"),"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["chinese","source","character","source_coda",
                                       "source_place","chinese_coda","chinese_place"])
        w.writeheader(); w.writerows(out)
    with io.open(os.path.join(REP,"step34_summary.txt"),"w",encoding="utf8") as f:
        f.write(txt+"\n")
    print("\nWrote data/derived/coda_place.csv and reports/step34_summary.txt")

if __name__=="__main__":
    main()
