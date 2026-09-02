#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 13 - Chinese -> Turkic channel, trained IN-DOMAIN.

The question this answers. Step 11 trained a reading-anchored channel on Sanskrit
and it worked in-domain (25.0% exact, 77.0% within-2) but collapsed on Turkic
(3.1% exact, 27.5% within-2, position accuracy 46% -> 10%). The diagnosis was
that fine-grained transcription conventions are language-specific and do not
transfer. Step 12 supplied 594 in-domain Turkic pairs to test that diagnosis.

If in-domain training clears the 3.1% / 27.5% out-of-domain baseline by a wide
margin, the diagnosis was right and the whole approach is sound - it simply needs
data in the right language. If it does not, something deeper is wrong.

ARCHITECTURE. Reading-anchored, as step 11 established:
  emission keyed on the EFEO syllable, backing off
      full syllable -> (onset, rime) -> onset -> global
  each syllable covering 1-3 Turkic segments, aligned by EM.

Reported with the same metrics as steps 7, 9, 11 so the comparison is honest.

Input:  data/derived/ligeti_turkic_chinese_pairs.csv  (from step 12)
Stdlib only.
"""
import csv, math, os, random, re, sys
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DER  = os.path.join(ROOT, "data", "derived")
REP  = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)
out = []
def log(s=""):
    print(s); out.append(s)

# ------------------------------------------------------------- EFEO parsing
# onsets longest-first so digraphs win
EFEO_ONSETS = ["tch'","tch","ts'","ts","ch","k'","p'","t'","ng","sh","ss",
               "k","p","t","s","h","m","n","l","y","w","f","j","r","g","b","d","z","v","c"]
def efeo_split(syl):
    s = syl.strip().lower()
    for o in EFEO_ONSETS:
        if s.startswith(o): return (o, s[len(o):])
    return ("", s)

# ---------------------------------------------------------- Turkic segments
TURK_MAP = {"ï":"i","ı":"i","ä":"e","ö":"o","ü":"u","ə":"e",
            "č":"C","š":"S","ž":"J","ǰ":"J","ŋ":"N","ɣ":"G","γ":"G",
            "y":"G",          # Ligeti writes gamma as y  (adiy = adiG)
            "ć":"C","ş":"S","ç":"C","ğ":"G","é":"e","á":"a","í":"i","ó":"o","ú":"u"}
def turk_segs(w):
    s = (w or "").strip()
    s = re.sub(r'[^\w\-ïıäöüəčšžǰŋɣγ]', '', s, flags=re.UNICODE)
    s = s.replace("-", "")
    return [TURK_MAP.get(c, c) for c in s if c.strip()]

log("=" * 72)
log(" STEP 13 - Chinese -> Turkic channel, trained in-domain")
log("=" * 72)
log()
src = os.path.join(DER, "ligeti_turkic_chinese_pairs.csv")
if not os.path.exists(src):
    log("FATAL: ligeti_turkic_chinese_pairs.csv missing. Run step 12."); sys.exit(1)

data = []
for r in csv.DictReader(open(src, encoding="utf-8-sig")):
    if (r.get("suspect") or "").strip(): continue
    syls = [s for s in (r["efeo_chinese"] or "").replace(" ", "-").split("-") if s]
    segs = turk_segs(r["turkic"])
    if not syls or len(segs) < 2: continue
    if len(segs) > 4*len(syls) + 3: continue
    data.append((syls, segs, r["turkic"], r["efeo_chinese"]))
log(f"usable pairs                : {len(data):,}")
sc = Counter(s for sy,_,_,_ in data for s in sy)
log(f"distinct EFEO syllables     : {len(sc)}")
log(f"observations per syllable   : {sum(sc.values())/max(1,len(sc)):.1f}")
log()

MAXCH, LOG0, P_SKIP, MINC = 3, -30.0, 0.02, 5
def lp(x): return math.log(x) if x > 0 else LOG0

class Channel:
    def __init__(self):
        self.full=defaultdict(Counter); self.orm=defaultdict(Counter)
        self.ons=defaultdict(Counter);  self.glob=Counter(); self.chunks=set()
    def add(self, syl, chunk, w=1):
        o, r = efeo_split(syl)
        self.chunks.add(chunk); self.glob[chunk]+=w
        self.full[syl][chunk]+=w; self.orm[(o,r)][chunk]+=w; self.ons[o][chunk]+=w
    def dist(self, syl):
        o, r = efeo_split(syl)
        for tbl, k in ((self.full,syl),(self.orm,(o,r)),(self.ons,o)):
            cc = tbl.get(k)
            if cc and sum(cc.values()) >= MINC: return cc
        return self.glob
    def p(self, syl, chunk):
        cc=self.dist(syl); tot=sum(cc.values())
        if not tot: return 0.0
        return (cc.get(chunk,0)+0.02)/(tot+0.02*max(1,len(self.chunks)))
    def topk(self, syl, k=5):
        cc=self.dist(syl); tot=sum(cc.values()) or 1
        return [(kk,v/tot) for kk,v in cc.most_common(k)]

def align(syls, segs, M):
    n,m=len(syls),len(segs); NEG=-1e18
    dp=[[NEG]*(m+1) for _ in range(n+1)]; bk=[[None]*(m+1) for _ in range(n+1)]
    dp[0][0]=0.0
    for i in range(n):
        for j in range(m+1):
            if dp[i][j]==NEG: continue
            for L in range(1,MAXCH+1):
                if j+L>m: break
                k=tuple(segs[j:j+L])
                v=dp[i][j]+lp(M.p(syls[i],k))
                if v>dp[i+1][j+L]: dp[i+1][j+L]=v; bk[i+1][j+L]=(i,j,k)
            v=dp[i][j]+lp(P_SKIP)
            if v>dp[i+1][j]: dp[i+1][j]=v; bk[i+1][j]=(i,j,None)
    if dp[n][m]==NEG: return NEG,[]
    i,j,al=n,m,[]
    while (i,j)!=(0,0):
        st=bk[i][j]
        if st is None: break
        pi,pj,k=st
        if k is not None: al.append((pi,k))
        i,j=pi,pj
    return dp[n][m],list(reversed(al))

def train(pairs, iters=10):
    M=Channel()
    for syls,segs,_,_ in pairs:
        for j in range(len(segs)):
            for L in range(1,MAXCH+1):
                if j+L<=len(segs):
                    M.add(syls[min(j,len(syls)-1)], tuple(segs[j:j+L]))
    for _ in range(iters):
        N=Channel()
        for syls,segs,_,_ in pairs:
            _,al=align(syls,segs,M)
            for ci,k in al: N.add(syls[ci],k)
        if not N.glob: break
        M=N
    return M

def editdist(a,b):
    if a==b: return 0
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1): cur.append(min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
BEAM,TOPN,K=300,5,20
def decode(M,syls):
    beams=[((),0.0)]
    for s in syls:
        cs=M.topk(s,TOPN)
        if not cs: return []
        nxt=[(pre+kk,sc+math.log(pv)) for pre,sc in beams for kk,pv in cs if pv>0]
        nxt.sort(key=lambda t:-t[1]); beams=nxt[:BEAM]
    best={}
    for wds,sc in beams:
        t="".join(wds)
        if t not in best or sc>best[t]: best[t]=sc
    items=sorted(best.items(), key=lambda kv:-kv[1])[:K]
    m=max(s for _,s in items); tot=sum(math.exp(s-m) for _,s in items)
    return [(w, math.exp(s-m)/tot) for w,s in items]

random.seed(11); random.shuffle(data)
cut=int(0.85*len(data)); tr,te = data[:cut], data[cut:]
log(f"split: {len(tr)} train / {len(te)} held out")
seen={s for sy,_,_,_ in tr for s in sy}
oov=sum(1 for sy,_,_,_ in te for s in sy if s not in seen)
tot_s=sum(len(sy) for sy,_,_,_ in te)
log(f"held-out syllable OOV rate: {oov}/{tot_s} = {100*oov/max(1,tot_s):.1f}%  "
    f"(handled by the onset/rime backoff)")
log()
M=train(tr)

pos=t1=t3=0; n=ex=e1=e2=0; tot=0.0
hits={k:0 for k in (1,3,5,10,20)}
for syls,segs,turk,efeo in te:
    _,al=align(syls,segs,M)
    for ci,gold in al:
        cand=M.topk(syls[ci],3)
        if not cand: continue
        pos+=1; names=[k for k,_ in cand]
        t1+=(names[0]==gold); t3+=(gold in names)
    got=decode(M,syls)
    if not got: continue
    n+=1; gold="".join(segs); forms=[w for w,_ in got]
    for k in hits:
        if gold in forms[:k]: hits[k]+=1
    d=min(editdist(w,gold) for w in forms)
    ex+=(d==0); e1+=(d<=1); e2+=(d<=2); tot+=d/max(len(gold),1)

log("-"*72)
log(" RESULTS on held-out Turkic")
log("-"*72)
if pos: log(f"  position: exact chunk top-1 {100*t1/pos:.1f}%   top-3 {100*t3/pos:.1f}%   (n={pos})")
if n:
    log(f"  whole-form top-k exact: " + "  ".join(f"top-{k} {100*hits[k]/n:.1f}%" for k in (1,5,20)))
    log(f"  best-of-top-20: exact {100*ex/n:.1f}%   within1 {100*e1/n:.1f}%   "
        f"within2 {100*e2/n:.1f}%")
    log(f"  mean normalised edit distance: {tot/n:.3f}   (n={n})")
log()
log("  THE COMPARISON THAT MATTERS - same architecture, same metrics:")
log("    step 11, Sanskrit-trained, tested on TURKIC (out-of-domain):")
log("        exact  3.1%   within1  6.9%   within2 27.5%   position top-1  9.8%")
log("    step 11, Sanskrit-trained, tested on Sanskrit (in-domain):")
log("        exact 25.0%   within1 57.9%   within2 77.0%   position top-1 46.3%")
log(f"    step 13, TURKIC-trained, tested on Turkic (in-domain):")
log(f"        exact {100*ex/max(1,n):4.1f}%   within1 {100*e1/max(1,n):4.1f}%   "
    f"within2 {100*e2/max(1,n):4.1f}%   position top-1 {100*t1/max(1,pos):4.1f}%")
log()
gain = 100*ex/max(1,n) - 3.1
if gain >= 10:
    log(f"  VERDICT: in-domain training beats the out-of-domain baseline by "
        f"{gain:+.1f} points")
    log("  on exact match. The step-11 diagnosis was right - the collapse was about")
    log("  the training language, not the method. A Chinese->Turkic channel works.")
elif gain >= 4:
    log(f"  VERDICT: a real but modest gain ({gain:+.1f} points). Direction confirmed,")
    log("  magnitude limited by 594 pairs. More Turkic data would help; Qi Hongtao")
    log("  and the remaining Ligeti pages are where it would come from.")
else:
    log(f"  VERDICT: in-domain training does NOT rescue this ({gain:+.1f} points).")
    log("  That contradicts the step-11 diagnosis and points at something deeper -")
    log("  most likely that 594 pairs is simply too few whatever the language.")
log()
log("SAMPLE - held-out reconstructions:")
for syls,segs,turk,efeo in te[:14]:
    got=decode(M,syls,)
    if not got: continue
    gold="".join(segs)
    mark="OK " if got[0][0]==gold else "   "
    log(f"  {mark}{efeo[:22]:22s} gold={gold:14s} -> " +
        ", ".join(f"{w}({p:.2f})" for w,p in got[:3]))

with open(os.path.join(DER,"turkic_channel_emissions.csv"),"w",newline="",encoding="utf-8-sig") as f:
    w=csv.writer(f); w.writerow(["efeo_syllable","turkic_segments","p"])
    for s in sorted(sc):
        for k,v in M.topk(s,6):
            if v>=0.01: w.writerow([s,"".join(k),round(v,4)])
log()
log("Written to data/derived/turkic_channel_emissions.csv")
with open(os.path.join(REP,"step13_summary.txt"),"w",encoding="utf-8") as f:
    f.write("\n".join(out)+"\n")
print("\nSummary written to reports/step13_summary.txt")
