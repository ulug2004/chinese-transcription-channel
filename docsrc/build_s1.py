# -*- coding: utf-8 -*-
import csv, io, html, sys, os
sys.path.insert(0,".")
from s1_rows import REMARK

CSV="/root/art/author_proposals.csv"
rows=list(csv.DictReader(io.open(CSV,encoding="utf-8-sig")))
by={r["chinese"]:r for r in rows}

RULERS=["頭曼","冒頓","稽粥","軍臣","詹師廬","呴犁湖","伊稚斜","烏維","且鞮侯","狐鹿姑","壺衍鞮",
        "虛閭權渠","握衍朐鞮","呼韓邪","郅支"]
RUODI=["若鞮","復株累若鞮","搜諧若鞮","車牙若鞮","烏珠留若鞮","烏累若鞮","呼都而尸道皋若鞮"]
CLAN=["虛連題","攣鞮"]   # the readable three-character form first, then the fragment
TITLES=["單于","撑犁孤塗單于","撑犁","孤塗","屠耆","谷蠡","當戶","閼氏","骨都侯","且渠","徑路","服匿","甌脫","胡祿"]
ETHNO=["匈奴","羯"]

def esc(x): return html.escape(x or "")

def table(keys, num, title, cap):
    out=['<h2 class="sec"><span class="n">S1.%d</span><span class="t">%s</span></h2>'%(num+5,title),
         '<div class="tablewrap"><table>',
      '<thead><tr>',
      '<th>Form, as written<br>in the histories</th>',
      '<th>Later Han reading of those<br>characters (Schuessler)</th>',
      '<th>The same reading in<br>Turkish orthography</th>',
      '<th>Reading we<br>propose</th>',
      '<th>Sense we propose<br>for that reading</th>',
      '</tr></thead><tbody>']
    for k in keys:
        r=by[k]
        out.append('<tr><td class="han2">%s<span class="py">%s</span></td>'
                   '<td class="num">%s</td><td class="num">%s</td>'
                   '<td class="prop">%s</td><td>%s</td></tr>'
                   %(esc(k),esc(r["pinyin"]),mark(k, r["later_han"]),
                     esc(r["turkish_render"]),esc(r["proposed_name"]),esc(r["proposed_sense"])))
        ph,rs = REMARK[k]
        out.append('<tr class="rem"><td colspan="5">'
                   '<span class="lab">Phonetics</span>%s<br>'
                   '<span class="lab">Reason</span>%s</td></tr>'%(ph,rs))
    out.append('</tbody></table></div>')
    out.append('<p class="cap"><span class="tnum">Table S%d</span>%s</p>'%(num+1,cap))
    return "\n".join(out)

# --- polyphony marking -------------------------------------------------
import collections as _c
_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDS = [os.path.join(_HERE, "..", "data", "external", "LHantab.tsv"),
          os.path.join(_HERE, "data", "external", "LHantab.tsv"),
          "/mnt/user-data/uploads/claude/names/data/external/LHantab.tsv"]
_LHTAB = next((x for x in _CANDS if os.path.exists(x)), _CANDS[0])
def _load_poly():
    n=_c.Counter(); seen=set()
    with io.open(_LHTAB, encoding="utf8", errors="ignore") as f:
        for x in csv.DictReader(f, delimiter="\t"):
            z=(x.get("zi") or "").strip(); sy=(x.get("syl_bok") or "").strip()
            if z and sy and (z,sy) not in seen:
                seen.add((z,sy)); n[z]+=1
    alts=_c.defaultdict(list)
    with io.open(_LHTAB, encoding="utf8", errors="ignore") as f:
        for x in csv.DictReader(f, delimiter="\t"):
            z=(x.get("zi") or "").strip(); sy=(x.get("syl_bok") or "").strip()
            if z and sy and sy not in alts[z]: alts[z].append(sy)
    return {z for z,k in n.items() if k>1}, alts
POLY, ALTS = _load_poly()
DAG = '<span class="poly">&dagger;</span>'
def mark(chinese, reading):
    syls = (reading or "").split()
    if len(syls) != len(chinese): return reading
    return " ".join(sy + (DAG if ch in POLY else "") for ch, sy in zip(chinese, syls))
# -----------------------------------------------------------------------

BODY = []
BODY.append(table(RULERS,1,"Chanyu, in order of reign",
  "The fifteen rulers whose names are not built on the recurring element 若鞮. Reign order follows the <em>Shiji</em> and <em>Hanshu</em> as reproduced in Appendix A of the paper."))
BODY.append(table(RUODI,2,"The six <span class=\"han\">若鞮</span> compounds",
  "The recurring element itself, then the six later chanyu whose formal names end in it. Only the shared element is argued for in the paper; the material preceding it in each name is a proposal like any other in this supplement."))
BODY.append(table(CLAN,3,"The ruling clan name, in its two written forms",
  "攣鞮 in the <em>Shiji</em> and <em>Hanshu</em>, 虛連題 in the <em>Hou Hanshu</em>. Both are taken here as the same name, which is the usual view."))
BODY.append(table(TITLES,4,"Titles and lexical items",
  "The titles and the handful of common nouns the Chinese histories preserve, in the order of Appendix A. The lexical items are the more interesting group because some of them are glossed in the source, which means a proposal about them can in principle be checked."))
BODY.append(table(ETHNO,5,"Ethnonyms",
  "Group names rather than personal names, and subject to a further difficulty: a Chinese exonym need not transcribe anything the group called itself."))


# --- S1.11 the polyphonic characters -----------------------------------
used = {}
for k in RULERS+RUODI+CLAN+TITLES+ETHNO:
    r = by.get(k)
    if not r: continue
    syls = (r["later_han"] or "").split()
    if len(syls) != len(k): continue
    for ch, sy in zip(k, syls):
        if ch in POLY: used.setdefault(ch, (sy, [a for a in ALTS[ch] if a != sy]))
P = ['<h2 class="sec"><span class="n">S1.11</span><span class="t">Characters with more than one '
     'Later Han reading</span></h2>',
     '<div class="tablewrap"><table><thead><tr>'
     '<th>Character</th><th>Reading printed</th><th>Other readings in the table</th>'
     '<th>Items in which it appears</th></tr></thead><tbody>']
where = {}
for k in RULERS+RUODI+CLAN+TITLES+ETHNO:
    for ch in k:
        if ch in used: where.setdefault(ch, []).append(k)
for ch in sorted(used, key=lambda c: (-len(where.get(c,[])), c)):
    sy, alts = used[ch]
    P.append('<tr><td class="han2">%s</td><td class="num">%s</td><td class="num">%s</td>'
             '<td class="han2" style="font-size:.85em">%s</td></tr>'
             % (ch, sy, " &middot; ".join(alts), " ".join(where.get(ch, []))))
P.append('</tbody></table></div>')
P.append('<p class="cap"><span class="tnum">Table S7</span>Every character in the record for which '
         'Schuessler\'s table gives more than one Later Han reading, with the reading printed in '
         'Appendix A of the paper and the alternatives not used. Generated from '
         '<code>data/derived/polyphony.csv</code>, which the numbered script step 24 writes, so this '
         'table cannot drift from the repository. The daggers in the tables above mark these same '
         'polyphonic '
         'characters. Where an alternative would change a proposed reading, the entry for that item '
         'says so.</p>')
BODY.append("\n".join(P))
# -----------------------------------------------------------------------

print("rows covered:", sum(len(x) for x in (RULERS,RUODI,CLAN,TITLES,ETHNO)), "of", len(rows))
missing=set(by)-set(RULERS+RUODI+CLAN+TITLES+ETHNO)
print("missing:", missing)

# --- S1.12 the two reconstructions compared ----------------------------
_PD_CANDS = ["/root/art/period_depth.csv",
             os.path.join(_HERE, "data", "derived", "period_depth.csv"),
             "/mnt/user-data/uploads/claude/names/data/derived/period_depth.csv"]
_PD = next((x for x in _PD_CANDS if os.path.exists(x)), None)
if _PD:
    pd = list(csv.DictReader(io.open(_PD, encoding="utf-8-sig")))
    diff = [r for r in pd if r["differs_in"] != "same"]
    same = len(pd) - len(diff)
    Q = ['<h2 class="sec"><span class="n">S1.12</span><span class="t">The two '
         'reconstructions of each character compared</span></h2>',
         '<div class="tablewrap"><table><thead><tr>'
         '<th>Character</th><th>Later Han<br>(Schuessler)</th>'
         '<th>Old Chinese<br>(Baxter &amp; Sagart)</th>'
         '<th>Onset class</th><th>Coda class</th></tr></thead><tbody>']
    for r in diff:
        on = ("%s &rarr; %s" % (r["lh_onset"], r["oc_onset"])
              if r["lh_onset"] != r["oc_onset"] else "&mdash;")
        cd = ("%s &rarr; %s" % (r["lh_coda"], r["oc_coda"])
              if r["lh_coda"] != r["oc_coda"] else "&mdash;")
        Q.append('<tr><td class="han2">%s</td><td class="num">%s</td>'
                 '<td class="num">%s</td><td>%s</td><td>%s</td></tr>'
                 % (r["char"], esc(r["later_han"]), esc(r["old_chinese"]), on, cd))
    Q.append('</tbody></table></div>')
    Q.append('<p class="cap"><span class="tnum">Table S8</span>The %d characters of the record, '
             'of the %d present in both reconstructions, where the two give a different class of '
             'segment in at least one position; the other %d agree. This is the measurement §11 of '
             'the paper reports, at 37%%. It is not a correction to Appendix A: Baxter and Sagart '
             'reconstruct a stage several centuries before the transcriptions and Schuessler one '
             'several centuries after, so the two bracket the moment of writing rather than dating '
             'it, and this table is the width of that bracket. Their <i>*-s</i> and <i>*-\u0294</i> '
             'are treated as having become tones by the Han and are not counted as codas, and a '
             'trailing <i>*-j</i> or <i>*-w</i> is read as the offglide of a diphthong rather than '
             'as a consonant. Generated from <code>data/derived/period_depth.csv</code>, which the '
             'numbered script step 43 writes.</p>' % (len(diff), len(pd), same))
    BODY.append("\n".join(Q))

io.open("s1_tables.html","w",encoding="utf8").write("\n\n".join(BODY))
