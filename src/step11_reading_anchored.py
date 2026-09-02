#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 11 - reading-anchored channel: the experiment that decides whether the
Xiongnu names are reachable at all.

Step 10 established that observations per character is the binding variable, and
the Xiongnu material sits at 1.4 - far too sparse for a character-keyed channel
(Sanskrit 5.0, Mongolian 60.8). No search, prior or architecture recovers from
that.

The fix is to stop keying on the CHARACTER and key on its RECONSTRUCTED LATER HAN
READING instead, decomposed into (initial, vowel, coda), with backoff:

        full reading  ->  (initial, vowel)  ->  initial  ->  global

Why that changes the arithmetic: a Xiongnu character that never appears in a
Buddhist transcription may still have a READING that appears, carried by some
other character. Evidence pools across every character sharing a reading, and at
the backed-off levels coverage approaches complete. Linguistically this is also
the more honest object - a transcription channel IS a phonology-to-phonology
mapping, not a character lookup table.

Reports, in order:
  1. COVERAGE - what fraction of Xiongnu characters are reachable at each level
  2. ACCURACY at Han-era data volume, against the two earlier architectures
  3. the Xiongnu names decoded, if and only if the accuracy justifies it

Stdlib only. Needs LHantab.tsv, Unihan.zip, and step 1 output.
"""
import csv, math, os, random, re, sys, zipfile
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT  = os.path.join(ROOT, "data", "external")
DER  = os.path.join(ROOT, "data", "derived")
DL   = os.path.join(ROOT, "Downloads")
REP  = os.path.join(ROOT, "reports")
os.makedirs(REP, exist_ok=True)
out = []
def log(s=""):
    print(s); out.append(s)
CJK = re.compile(r'[㐀-䶿一-鿿]')

# --------------------------------------------------- Later Han reading parse
TONES = "ᴬᴮᶜᴰ"
LH_C = ['tsʰ','tśʰ','dź','tś','ts','dz','kʰ','pʰ','tʰ','ṭʰ','ḍ','ṭ','ṇ','ṣ','ś','ź',
        'ŋ','ɦ','ʔ','x','γ','k','g','p','b','m','t','d','n','s','z','h','j','w','l','r','f','v']
LH_V = set("aeiouɑɔəɛɨɯyœøæ")
def parse_reading(s):
    """'mɑnᶜ' -> ('m','ɑ','n'). Tone stripped: Chinese tone carried no information
       about the foreign source segment."""
    s = "".join(c for c in (s or "") if c not in TONES).strip()
    if not s: return None
    init = ""
    for c in LH_C:
        if s.startswith(c): init = c; break
    rest = s[len(init):]
    i = 0
    while i < len(rest) and rest[i] not in LH_V: i += 1
    j = i
    while j < len(rest) and rest[j] in LH_V: j += 1
    return (init, rest[i:j], rest[j:])

def load_lhan():
    p = os.path.join(EXT, "LHantab.tsv")
    if not os.path.exists(p):
        log("FATAL: LHantab.tsv missing from data/external/."); sys.exit(1)
    rows = list(csv.reader(open(p, encoding="utf-8"), delimiter="\t"))
    h = rows[0]; zi = h.index("zi") if "zi" in h else 1
    sy = h.index("syl_bok") if "syl_bok" in h else len(h)-2
    d = defaultdict(list)
    for r in rows[1:]:
        if len(r) > max(zi, sy) and len(r[zi]) == 1 and r[sy]: d[r[zi]].append(r[sy])
    return d
def load_variants():
    zp = os.path.join(EXT, "Unihan.zip"); eq = defaultdict(set)
    if not os.path.exists(zp): return eq
    F = {"kSemanticVariant","kZVariant","kSimplifiedVariant","kTraditionalVariant"}
    try:
        with zipfile.ZipFile(zp) as z:
            nm = next((x for x in z.namelist() if x.endswith("Unihan_Variants.txt")), None)
            if not nm: return eq
            for raw in z.open(nm):
                L = raw.decode("utf-8","replace")
                if L.startswith("#") or not L.strip(): continue
                q = L.rstrip("\n").split("\t")
                if len(q) < 3 or q[1] not in F: continue
                try: a = chr(int(q[0][2:],16))
                except Exception: continue
                for t in re.findall(r"U\+([0-9A-Fa-f]+)", q[2]):
                    b = chr(int(t,16)); eq[a].add(b); eq[b].add(a)
    except Exception: return defaultdict(set)
    return eq

log("=" * 74)
log(" STEP 11 - reading-anchored channel")
log("=" * 74)
log()
LHAN = load_lhan(); VAR = load_variants()
def reading_of(c):
    rs = LHAN.get(c)
    if not rs:
        for v in VAR.get(c, ()):
            if v in LHAN: rs = LHAN[v]; break
    if not rs: return None
    return parse_reading(rs[0])
log(f"Later Han table: {len(LHAN):,} characters; Unihan variants: {len(VAR):,}")
log()

# ---------------------------------------------------------- Sanskrit data
SKT_C = ['kh','gh','ch','jh','ṭh','ḍh','th','dh','ph','bh',
         'k','g','ṅ','c','j','ñ','ṭ','ḍ','ṇ','t','d','n','p','b','m',
         'y','r','l','v','ś','ṣ','s','h','ṃ','ḥ']
SKT_V = ['ai','au','ā','ī','ū','ṝ','ṛ','ḹ','ḷ','a','i','u','e','o']
SMAP = {'kh':'k','gh':'g','ch':'C','jh':'J','ṭh':'t','ḍh':'d','th':'t','dh':'d',
        'ph':'p','bh':'b','ṅ':'N','ñ':'N','ṭ':'t','ḍ':'d','ṇ':'n','ś':'S','ṣ':'S',
        'ṃ':'N','ḥ':'h','c':'C','j':'J','ā':'a','ī':'i','ū':'u','ṝ':'r','ṛ':'r',
        'ḹ':'l','ḷ':'l','ai':'a','au':'a'}
def skt_segs(w):
    s=(w or "").strip().lower(); i=0; res=[]
    while i<len(s):
        for t in SKT_V+SKT_C:
            if s.startswith(t,i): res.append(SMAP.get(t,t)); i+=len(t); break
        else: i+=1
    return res

sp = os.path.join(DER, "nti_transcription_pairs.csv")
if not os.path.exists(sp):
    log("FATAL: nti_transcription_pairs.csv missing. Run step 1."); sys.exit(1)
data = []
for r in csv.DictReader(open(sp, encoding="utf-8-sig")):
    ch = CJK.findall(r["trad"] or ""); sg = skt_segs(r["skt"])
    if len(ch) >= 1 and 2 <= len(sg) <= 4*len(ch)+3: data.append((ch, sg))
log(f"Sanskrit training pairs: {len(data):,}")

# --------------------------------------------------------- 1. COVERAGE
log()
log("=" * 74)
log(" 1. COVERAGE - are the Xiongnu characters reachable?")
log("=" * 74)
log()
train_chars = Counter(c for ch,_ in data for c in ch)
LV_train = {}
for c in train_chars:
    r = reading_of(c)
    if r: LV_train.setdefault(r, 0); LV_train[r] += train_chars[c]
full_set = set(LV_train)
iv_set   = {(i,v) for (i,v,co) in full_set}
in_set   = {i for (i,v,co) in full_set}

xio = []
for fn in ("xiongnu_rulers_reconstructed.csv","xiongnu_titles_lexicon_reconstructed.csv"):
    fp = os.path.join(DER, fn)
    if os.path.exists(fp):
        for r in csv.DictReader(open(fp, encoding="utf-8-sig")):
            ch = CJK.findall(r.get("chinese") or "")
            if ch: xio.append((r.get("chinese",""), ch, r.get("proposed_reading","")))
xchars = sorted({c for _,ch,_ in xio for c in ch})
log(f"Distinct Xiongnu characters: {len(xchars)}")
lvl = Counter()
for c in xchars:
    if c in train_chars: lvl["character seen directly"] += 1; continue
    r = reading_of(c)
    if r is None: lvl["no Later Han reading"] += 1
    elif r in full_set: lvl["full reading seen"] += 1
    elif (r[0], r[1]) in iv_set: lvl["initial+vowel seen"] += 1
    elif r[0] in in_set: lvl["initial seen"] += 1
    else: lvl["nothing above global"] += 1
ORDER = ["character seen directly","full reading seen","initial+vowel seen",
         "initial seen","nothing above global","no Later Han reading"]
cum = 0
for k in ORDER:
    v = lvl.get(k, 0)
    if not v: continue
    cum += v
    log(f"  {k:26s} {v:4d}  ({100*v/len(xchars):5.1f}%)   cumulative {100*cum/len(xchars):5.1f}%")
log()
direct = lvl.get("character seen directly",0)
log(f"Character-keyed channel would cover {100*direct/len(xchars):.1f}% of Xiongnu characters.")
log(f"Reading-anchored with backoff covers "
    f"{100*(len(xchars)-lvl.get('no Later Han reading',0)-lvl.get('nothing above global',0))/len(xchars):.1f}%.")
log()

# ------------------------------------------------------- 2. the model
MAXCH = 3; LOG0 = -30.0; P_SKIP = 0.02
def lp(x): return math.log(x) if x>0 else LOG0
MINC = 6            # use a level only if it has this many observations

class Channel:
    """Hierarchical emission keyed on the Later Han reading, with backoff."""
    def __init__(self):
        self.full=defaultdict(Counter); self.iv=defaultdict(Counter)
        self.ini=defaultdict(Counter);  self.glob=Counter()
        self.chunks=set()
    def key(self, c):
        return reading_of(c)
    def add(self, c, chunk, w=1):
        r=self.key(c)
        self.chunks.add(chunk); self.glob[chunk]+=w
        if r is None: return
        self.full[r][chunk]+=w; self.iv[(r[0],r[1])][chunk]+=w; self.ini[r[0]][chunk]+=w
    def dist(self, c):
        r=self.key(c)
        for tbl,k in ((self.full,r),(self.iv,(r[0],r[1]) if r else None),
                      (self.ini,r[0] if r else None)):
            if k is None: continue
            cc=tbl.get(k)
            if cc and sum(cc.values())>=MINC: return cc
        return self.glob
    def p(self, c, chunk):
        cc=self.dist(c); tot=sum(cc.values())
        if not tot: return 0.0
        return (cc.get(chunk,0)+0.02)/(tot+0.02*max(1,len(self.chunks)))
    def topk(self, c, k=5):
        cc=self.dist(c); tot=sum(cc.values()) or 1
        return [(kk,v/tot) for kk,v in cc.most_common(k)]

def align(ch, sg, model):
    n,m=len(ch),len(sg); NEG=-1e18
    dp=[[NEG]*(m+1) for _ in range(n+1)]; bk=[[None]*(m+1) for _ in range(n+1)]
    dp[0][0]=0.0
    for i in range(n):
        for j in range(m+1):
            if dp[i][j]==NEG: continue
            for L in range(1,MAXCH+1):
                if j+L>m: break
                k=tuple(sg[j:j+L])
                v=dp[i][j]+lp(model.p(ch[i],k))
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

def train_model(train, iters=8):
    M=Channel()
    for ch,sg in train:                       # init: uniform over observed chunks
        for j in range(len(sg)):
            for L in range(1,MAXCH+1):
                if j+L<=len(sg): M.add(ch[min(j,len(ch)-1)], tuple(sg[j:j+L]))
    for _ in range(iters):
        N=Channel()
        for ch,sg in train:
            _,al=align(ch,sg,M)
            for ci,k in al: N.add(ch[ci],k)
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
BEAM,TOPN,K=250,5,20
def decode(M,ch):
    beams=[((),0.0)]
    for c in ch:
        cs=M.topk(c,TOPN)
        if not cs: return []
        nxt=[(pre+kk,s+math.log(pv)) for pre,s in beams for kk,pv in cs if pv>0]
        nxt.sort(key=lambda t:-t[1]); beams=nxt[:BEAM]
    best={}
    for w,s in beams:
        t="".join(w)
        if t not in best or s>best[t]: best[t]=s
    return [(w,s) for w,s in sorted(best.items(), key=lambda kv:-kv[1])[:K]]

log("=" * 74)
log(" 2. ACCURACY at Han-era data volume")
log("=" * 74)
log()
random.seed(7); random.shuffle(data)
cut=int(0.85*len(data)); tr,te = data[:cut], data[cut:]
M = train_model(tr)
pos=t1=t3=0; n=ex=e1=e2=0; tot=0.0
for ch,sg in te:
    _,al=align(ch,sg,M)
    for ci,gold in al:
        cand=M.topk(ch[ci],3)
        if not cand: continue
        pos+=1; names=[k for k,_ in cand]
        t1+=(names[0]==gold); t3+=(gold in names)
    got=decode(M,ch)
    if not got: continue
    n+=1; gold="".join(sg)
    d=min(editdist(w,gold) for w,_ in got)
    ex+=(d==0); e1+=(d<=1); e2+=(d<=2); tot+=d/max(len(gold),1)
log(f"  {len(tr):,} train / {len(te):,} test")
if pos: log(f"  position top-1 {100*t1/pos:.1f}%   top-3 {100*t3/pos:.1f}%")
if n:
    log(f"  whole-form exact {100*ex/n:.1f}%   within1 {100*e1/n:.1f}%   "
        f"within2 {100*e2/n:.1f}%   mean ned {tot/n:.3f}")
log()
log("  Same data, earlier architectures:")
log("    character-keyed, syllable units   exact  8.2%  within1 17.4%  within2 32.8%")
log("    character-keyed, segmental units  exact  8.8%  within1 22.5%  within2 39.2%")
log(f"    reading-anchored, segmental       exact {100*ex/max(1,n):5.1f}%  "
    f"within1 {100*e1/max(1,n):5.1f}%  within2 {100*e2/max(1,n):5.1f}%")
log()
better = (100*ex/max(1,n)) - 8.8
log(f"  Effect of reading-anchoring: {better:+.1f} points on exact match.")
log()

# ------------------------------- 2b. OUT-OF-DOMAIN: the number that matters
# The 858-pair Sanskrit test set is IN-DOMAIN: same period, same source language,
# same conventionalised Buddhist transcription practice. The Xiongnu material
# shares none of that. Out-of-domain accuracy on the Ming Uyghur pairs is the
# honest proxy, and it - not the in-domain figure - decides whether per-name
# reconstructions may be reported.
UYM = {"č":"C","š":"S","ž":"J","ǰ":"J","ŋ":"N","ɣ":"G","ġ":"G","ḳ":"q"}
def uy_segs(w):
    s = (w or "").strip()
    for a,b in UYM.items(): s = s.replace(a,b)
    s = s.replace("-"," ").replace("(","").replace(")","")
    s = re.sub(r'[^A-Za-zäöüïıə ]','',s)
    return [c for c in s if c != " "]

uy = []
up = os.path.join(DER, "uyghur_chinese_pairs.csv")
if os.path.exists(up):
    for r in csv.DictReader(open(up, encoding="utf-8-sig")):
        ch = CJK.findall(r["chinese"] or "")
        sg = uy_segs((r["uyghur_variants"] or "").split("|")[-1])
        if len(ch) >= 1 and 2 <= len(sg) <= 4*len(ch)+3: uy.append((ch, sg))

log("=" * 74)
log(" 2b. OUT-OF-DOMAIN accuracy (Ming Uyghur) - the decision-relevant number")
log("=" * 74)
log()
ood = dict(n=0, exact=0.0, w1=0.0, w2=0.0, ned=0.0, pp1=0.0)
if not uy:
    log("  No Uyghur pairs found - run RUN-uyghur.bat. Cannot judge out-of-domain.")
else:
    pos2=u1=0; n2=x2=a1=a2=0; t2=0.0
    for ch,sg in uy:
        _,al = align(ch,sg,M)
        for ci,gold in al:
            cand=M.topk(ch[ci],1)
            if not cand: continue
            pos2+=1; u1 += (cand[0][0]==gold)
        got=decode(M,ch)
        if not got: continue
        n2+=1; gold="".join(sg)
        d=min(editdist(w,gold) for w,_ in got)
        x2+=(d==0); a1+=(d<=1); a2+=(d<=2); t2+=d/max(len(gold),1)
    if n2:
        ood=dict(n=n2, exact=100*x2/n2, w1=100*a1/n2, w2=100*a2/n2, ned=t2/n2,
                 pp1=(100*u1/pos2 if pos2 else 0))
        log(f"  forms scored {n2}   position top-1 {ood['pp1']:.1f}%")
        log(f"  whole-form exact {ood['exact']:.1f}%   within1 {ood['w1']:.1f}%   "
            f"within2 {ood['w2']:.1f}%   mean ned {ood['ned']:.3f}")
        log()
        log("  In-domain vs out-of-domain, same model:")
        log(f"    in-domain  (Sanskrit) : exact {100*ex/max(1,n):5.1f}%  "
            f"within2 {100*e2/max(1,n):5.1f}%")
        log(f"    out-of-domain (Uyghur): exact {ood['exact']:5.1f}%  "
            f"within2 {ood['w2']:5.1f}%")
        log()
        log("  The gap between those two rows is what the Xiongnu names inherit.")
log()

# --------------------------------------------------- 3. Xiongnu, if warranted
log("=" * 74)
log(" 3. XIONGNU NAMES")
log("=" * 74)
log()
if ood["n"] == 0 or ood["w2"] < 45:
    log(f"  Out-of-domain within-2 is {ood['w2']:.1f}% (threshold 45%), so per-name")
    log("  reconstructions are NOT reported - they would be noise dressed as")
    log("  results. Note the in-domain figure is much higher; using it as the gate")
    log("  would have been self-flattering, since the Xiongnu material shares")
    log("  neither period, source language, nor transcription convention with the")
    log("  Buddhist corpus.")
    log()
    log("  What the coverage result does buy: every Xiongnu character is now")
    log("  reachable, so the pipeline is no longer blocked structurally. The")
    log("  remaining gap is data volume for the Han-era channel, and step 10's")
    log("  curve says how much would be needed.")
else:
    rows_out=[]
    log(f"  {'name':8s} {'top candidates':40s} literature")
    for orig, ch, lit in xio:
        got=decode(M,ch)
        if not got: continue
        m0=max(s for _,s in got)
        tt=sum(math.exp(s-m0) for _,s in got)
        cands=[(w, math.exp(s-m0)/tt) for w,s in got[:4]]
        rows_out.append({"chinese":orig,
                         "candidates":" | ".join(f"{w} {p:.3f}" for w,p in cands),
                         "proposed_in_literature":lit})
        log(f"  {orig:8s} " +
            f"{' '.join(f'{w}({p:.2f})' for w,p in cands):40s} {lit}")
    with open(os.path.join(DER,"xiongnu_reading_anchored.csv"),"w",newline="",
              encoding="utf-8-sig") as f:
        if rows_out:
            w=csv.DictWriter(f,fieldnames=list(rows_out[0].keys()))
            w.writeheader(); w.writerows(rows_out)
    log()
    log("  Written to data/derived/xiongnu_reading_anchored.csv")

with open(os.path.join(REP,"step11_summary.txt"),"w",encoding="utf-8") as f:
    f.write("\n".join(out)+"\n")
print("\nSummary written to reports/step11_summary.txt")
