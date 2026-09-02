# -*- coding: utf-8 -*-
import io,re
def rx(text):
    "plain text -> regex tolerant of line breaks between words"
    return r"\s+".join(re.escape(w) for w in text.split())
def apply(path,pairs,label=""):
    s=io.open(path,encoding="utf8").read(); ok=0; bad=[]
    for old,new in pairs:
        pat=re.compile(rx(old))
        n=len(pat.findall(s))
        if n==1: s=pat.sub(lambda m:new,s,count=1); ok+=1
        else: bad.append((n,old[:64]))
    io.open(path,"w",encoding="utf8").write(s)
    print("%s applied %d, missed %d"%(label,ok,len(bad)))
    for n,o in bad: print("   MISS(%d) %s"%(n,o))
