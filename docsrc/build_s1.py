# -*- coding: utf-8 -*-
import csv, io, html, sys
sys.path.insert(0,".")
from s1_rows import REMARK

CSV="/root/art/author_proposals.csv"
rows=list(csv.DictReader(io.open(CSV,encoding="utf8")))
by={r["chinese"]:r for r in rows}

RULERS=["頭曼","冒頓","稽粥","軍臣","詹師廬","呴犁湖","伊稚斜","烏維","且鞮侯","狐鹿姑","壺衍鞮",
        "虛閭權渠","握衍朐鞮","呼韓邪","郅支"]
RUODI=["若鞮","復株累若鞮","搜諧若鞮","車牙若鞮","烏珠留若鞮","烏累若鞮","呼都而尸道皋若鞮"]
CLAN=["攣鞮","虛連題"]
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
                   %(esc(k),esc(r["pinyin"]),esc(r["later_han"]),
                     esc(r["turkish_render"]),esc(r["proposed_name"]),esc(r["proposed_sense"])))
        ph,rs = REMARK[k]
        out.append('<tr class="rem"><td colspan="5">'
                   '<span class="lab">Phonetics</span>%s<br>'
                   '<span class="lab">Reason</span>%s</td></tr>'%(ph,rs))
    out.append('</tbody></table></div>')
    out.append('<p class="cap"><span class="tnum">Table S%d</span>%s</p>'%(num+1,cap))
    return "\n".join(out)

BODY = []
BODY.append(table(RULERS,1,"Chanyu, in order of reign",
  "The fifteen rulers whose names are not built on the recurring element 若鞮. Reign order follows the <em>Shiji</em> and <em>Hanshu</em> as reproduced in Appendix A of the paper."))
BODY.append(table(RUODI,2,"The six <span class=\"han\">若鞮</span> compounds",
  "The recurring element itself, then the six later chanyu whose formal names end in it. Only the shared element is argued for in the paper; the material preceding it in each name is a proposal like any other in this file."))
BODY.append(table(CLAN,3,"The ruling clan name, in its two written forms",
  "攣鞮 in the <em>Shiji</em> and <em>Hanshu</em>, 虛連題 in the <em>Hou Hanshu</em>. Both are taken here as the same name, which is the usual view."))
BODY.append(table(TITLES,4,"Titles and lexical items",
  "The titles and the handful of common nouns the Chinese histories preserve, in the order of Appendix A. The lexical items are the more interesting group because some of them are glossed in the source, which means a proposal about them can in principle be checked."))
BODY.append(table(ETHNO,5,"Ethnonyms",
  "Group names rather than personal names, and subject to a further difficulty: a Chinese exonym need not transcribe anything the group called itself."))
print("rows covered:", sum(len(x) for x in (RULERS,RUODI,CLAN,TITLES,ETHNO)), "of", len(rows))
missing=set(by)-set(RULERS+RUODI+CLAN+TITLES+ETHNO)
print("missing:", missing)
io.open("s1_tables.html","w",encoding="utf8").write("\n\n".join(BODY))
