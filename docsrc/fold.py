# -*- coding: utf-8 -*-
import json, io, re, sys
sys.path.insert(0,"/root/art")
import match

REPAIR = [
 ("following.Three","following. Three"),
 ("avaiable","available"),
 ("parseable..","parseable."),
 ("0.117..","0.117."),
 ("pairs.We kept","pairs. We kept"),
 ("operation ofkeeping","operation of keeping"),
 ("languages.This","languages. This"),
 ("50%.Thisis recorded","50%. This is recorded"),
 ("hasnever been","has never been"),
 ("Ming era which istwelve","Ming era, which is twelve"),
 ("gap. Ee took","gap. We took"),
 ("used.Blending","used. Blending"),
 ("87% whichmeans","87%, which means"),
 ("for themselvesregardless","for themselves regardless"),
 ("made.The selection bias §6.3 measures are removed","made. The selection bias §6.3 measures is removed"),
 ("otjer hand,","other hand,"),
 ("that Turkiccandidate survives","that the Turkic candidate survives"),
 ("suggests.Clauson","suggests. Clauson"),
 ("answer the question: the field","answer the question the field"),
 ("We had two approaches failed before","We had two approaches fail before"),
 ("verification of  scoring","verification, scoring"),
 ("check providing that  the filter","check that the filter"),
 ("§6 need  dictionaries","§6 need dictionaries"),
 ("no downloadable dataset either, so","no downloadable dataset, so"),
 ("Three of four holds,","Three of four hold,"),
 ("reads kırpa:k and corrected in the margin","reads kırpa:k and is corrected in the margin"),
 ("with nothing supplied kıñrak, which means","with nothing supplied; kıñrak, which means"),
 ("future work  need to go next","future work needs to go next"),
 ("three notations. So of the apparent","three notations. So some of the apparent"),
 ("Reproducibility has software dependency","Reproducibility has a software dependency"),
 ("record accompany this submission","record accompanies this submission"),
 ("(13.6 %)","(13.6%)"),
 ("the count above (13%)","the count above (13.6%)"),
]
def repair(t):
    for a,b in REPAIR: t=t.replace(a,b)
    return re.sub(r"  +"," ",t).strip()

def core(old,new):
    """strip shared leading/trailing words; guarantee a non-empty core"""
    A=old.split(); B=new.split()
    i=0
    while i<len(A) and i<len(B) and A[i]==B[i]: i+=1
    j=0
    while j<len(A)-i and j<len(B)-i and A[len(A)-1-j]==B[len(B)-1-j]: j+=1
    if i>=len(A)-j and i>0:          # pure insertion: borrow one word of context
        i-=1
    return A[:i], A[i:len(A)-j], A[len(A)-j:], B[i:len(B)-j]

def build(pre,c_old,suf):
    P = match.rx(" ".join(pre)) + match.GAP if pre else ""
    S = match.GAP + match.rx(" ".join(suf)) if suf else ""
    C = match.rx(" ".join(c_old))
    return re.compile(P + "(" + C + ")" + S)

def main():
    pairs=json.load(open("paper_pairs.json"))
    s=io.open("paper.html",encoding="utf8").read()
    applied=0; manual=[]
    for i,p in enumerate(pairs):
        old=p["old"]; new=repair(p["new"])
        pre,c_old,suf,c_new=core(old,new)
        if not c_old:
            manual.append((i,"empty core",old[:70])); continue
        if not pre and not suf:
            manual.append((i,"no anchor",old[:70])); continue
        ms=list(build(pre,c_old,suf).finditer(s))
        if len(ms)!=1:
            manual.append((i,"matches=%d"%len(ms),old[:70])); continue
        m=ms[0]
        if "<" in m.group(1):
            manual.append((i,"markup inside change",m.group(1)[:70])); continue
        s=s[:m.start(1)]+" ".join(c_new)+s[m.end(1):]
        applied+=1
    io.open("paper.html","w",encoding="utf8").write(s)
    print("applied: %d   manual: %d" % (applied,len(manual)))
    for i,why,t in manual: print("  #%3d  %-22s %s" % (i,why,t))

if __name__=='__main__':
    main()
