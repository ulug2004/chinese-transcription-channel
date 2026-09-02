# -*- coding: utf-8 -*-
"""
step23_liquid_coda.py -- how did a scribe write a source syllable ending in -r?

Later Han Chinese has no -r coda. A source syllable such as *tur* therefore had to be
written some other way, and the choice matters for reading names: 冒頓 kuət... no,
頓 tuənᶜ carries a written -n, so reading it as *tur* assumes -r was spelled with -n.
This counts what the scribes actually did, on the 1017 verified Sanskrit pairs.

Input : data/derived/nti_transcription_pairs.csv , data/external/LHantab.tsv
Output: data/derived/liquid_coda.csv , reports/step23_summary.txt

The syllabifier is a heuristic: each syllable is onset + vowel + the consonants up to
the last one before the next vowel. Pairs where it disagrees with the character count
are dropped rather than forced, so the sample is smaller than the corpus.
"""
import csv, io, os, sys, collections

HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
DER=os.path.join(ROOT,"data","derived"); EXT=os.path.join(ROOT,"data","external")
REP=os.path.join(ROOT,"reports")
V="aeiouāīūṛeoêôåæ"

def syllabify(w):
    pos=[i for i,c in enumerate(w) if c in V]
    if not pos: return []
    out=[]; prev_end=0
    for k,i in enumerate(pos):
        start=0 if k==0 else prev_end
        nxt=pos[k+1] if k+1<len(pos) else len(w)
        cons=w[i+1:nxt]
        keep=cons[:-1] if (k+1<len(pos) and len(cons)>=1) else cons
        end=i+1+len(keep); out.append(w[start:end]); prev_end=end
    return out

def main():
    lh=os.path.join(EXT,"LHantab.tsv"); pr=os.path.join(DER,"nti_transcription_pairs.csv")
    for p in (lh,pr):
        if not os.path.exists(p): sys.exit("Missing: %s"%p)
    LH={}
    with io.open(lh,encoding="utf8",errors="ignore") as f:
        for x in csv.DictReader(f,delimiter="\t"):
            z=x.get("zi") or ""
            if z and z not in LH: LH[z]=((x.get("con") or ""),(x.get("vow") or ""))
    with io.open(pr,encoding="utf-8-sig") as f:
        rows=[r for r in csv.DictReader(f)
              if r.get("align")=="exact" and r.get("n_chars")==r.get("n_syl")]
    n=collections.Counter(); out=[]; used=0
    for r in rows:
        zi=r["trad"]; skt=(r["skt"] or "").lower().replace("ṃ","m").replace("ṅ","n").replace("ñ","n")
        syl=syllabify(skt)
        if len(syl)!=len(zi): continue
        used+=1
        for ch,sy in zip(zi,syl):
            a=LH.get(ch)
            if not a: continue
            coda=(a[1] or "")[-1:]
            if sy.endswith("r") and len(sy)>1:
                key=coda if coda in "ptkmnŋ" else "open"
                n[key]+=1
                out.append({"chinese":ch,"sanskrit":r["skt"],"source_syllable":sy,
                            "lhan_vowel":a[1],"chinese_coda":key})
    t=sum(n.values()) or 1
    lines=["step 23 - how a source syllable in -r was written","",
           "Pairs usable after syllabification: %d"%used,
           "Source syllables ending in -r: %d"%t,""]
    for k,v in n.most_common():
        lines.append("  Chinese coda %-6s %4d  (%.0f%%)"%(k,v,100*v/t))
    lines += ["",
      "Reading: Later Han has no -r coda, so the scribe had to choose. He left the",
      "syllable open most often, and used a -t coda next. A -n coda for a source -r is",
      "the rarest option in the sample. That bears directly on 頓 tuənᶜ, whose -n is",
      "written: reading it as a source *tur* requires the rarest of the four choices.","",
      "Caveat: the syllabifier is a heuristic and the sample is small; treat the",
      "percentages as orders of magnitude, not as estimates with tight intervals."]
    txt="\n".join(lines); print(txt)
    if not os.path.isdir(REP): os.makedirs(REP)
    with io.open(os.path.join(DER,"liquid_coda.csv"),"w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["chinese","sanskrit","source_syllable","lhan_vowel","chinese_coda"])
        w.writeheader(); w.writerows(out)
    with io.open(os.path.join(REP,"step23_summary.txt"),"w",encoding="utf8") as f: f.write(txt+"\n")
    print("\nWrote data/derived/liquid_coda.csv and reports/step23_summary.txt")

if __name__=="__main__": main()
