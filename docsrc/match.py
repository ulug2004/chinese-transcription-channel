# -*- coding: utf-8 -*-
import re
TAG = r"(?:<[^>]*>)*"
GAP = r"(?:\s|<[^>]*>|&nbsp;)+"
CLS = {"'": "['’ʼ]", "’": "['’ʼ]",
       '"': '["“”]', "“": '["“”]', "”": '["“”]',
       "-": "[-‐‑]"}
def word_rx(w):
    out=[]
    for ch in w:
        out.append(CLS.get(ch, re.escape(ch)))
    return TAG.join(out)
def rx(text):
    return GAP.join(word_rx(w) for w in text.split())
def find(s, text):
    return list(re.finditer(rx(text), s))
