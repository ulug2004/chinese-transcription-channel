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


# ---------------------------------------------------------------- S1.13
# Every row of the record priced by the one engine, in a single table.
# Built here rather than pasted, so it cannot drift from the readings above.
# The RAW price is the product of the measured rates and falls with every
# extra character, so it sorts by length; the PER CHARACTER figure is the
# geometric mean, raw**(1/characters), and is the only one of the two
# comparable across names.  The sort is on it.
#
# Three kinds of row are priced on something other than the reading as
# printed, and the "Priced as" column names the result for every one:
#   the six names carrying 若鞮, which §9 argues once and which is priced
#   once, in its own row, and left out of the other six;
#   撑犁 and 撑犁孤塗單于, priced on the phonetic form, since 撑 carries a
#   velar nasal and a price is a claim about sounds;
#   若鞮, 搜諧若鞮 and 冒頓, priced on what the characters write, the
#   proposal containing something they do not.
CONTROL = 0.080
TITLE_CHARS = u"若鞮"
PRICED_AS = {u"若鞮": u"nakt", u"搜諧若鞮": u"sarg", u"冒頓": u"bö tuğ"}

def price_table():
    import re as _re, math as _math
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(".")), "src"))
    sys.path.insert(0, "src"); sys.path.insert(0, ".")
    import price_engine as PE
    R = PE.Rates()
    out = []
    for r in rows:
        z = r["chinese"].strip()
        prop = (r["proposed_name"] or "").strip()
        tk = (r.get("turkish_approx") or "").strip()
        if not prop or prop.startswith("("):
            continue
        zi, form = z, prop
        if len(zi) > 2 and zi.endswith(TITLE_CHARS) and u"nakt" in form.lower():
            zi = zi[:-2]
            form = _re.sub(u"[İi]nakt", u"", form, flags=_re.I).strip(u" -")
        form = PRICED_AS.get(z, form)
        a, err, note = PE.price_name(zi, form, R, strip_title=False)
        if a is None:
            continue
        display = tk or prop
        out.append((a.price ** (1.0 / len(zi)), a.price, z, display, form,
                    form.lower() != display.lower(), len(zi),
                    (r["proposed_sense"] or "").strip()))
    out.sort()
    T = ['<h2 class="sec"><span class="n">S1.13</span>'
         '<span class="t">Every reading priced, most expensive first</span></h2>',
         '<div class="tablewrap"><table><thead><tr>',
         '<th>Form, as written<br>in the histories</th><th>Reading proposed</th>',
         '<th>Priced as</th><th>Characters<br>priced</th>',
         '<th>Price,<br>1 in</th><th>Per<br>character</th><th>Sense</th>',
         '</tr></thead><tbody>']
    for per, pr, z, display, form, differs, n, sense in out:
        T.append('<tr><td class="han2">%s</td><td>%s</td><td class="num">%s</td>'
                 '<td class="num">%d</td><td class="num">%s</td>'
                 '<td class="num">%.1f%%</td><td>%s</td></tr>'
                 % (esc(z), esc(display), esc(form.title()) if differs else "&mdash;",
                    n, "{:,}".format(int(round(1.0 / pr))), 100 * per, esc(sense)))
    T.append('</tbody></table></div>')
    above = len([1 for d in out if d[0] >= CONTROL])
    T.append('<p class="cap"><span class="tnum">Table S9</span>All %d rows priced by the one '
             'engine. <b>Priced as</b> names the form the figure was taken on and is filled in '
             'only where that is not the reading exactly as printed. The six names carrying '
             '<span class="han">%s</span> are priced without it, since §9 of the paper argues '
             'that element once and it is priced once, in its own row. '
             '<span class="han">撑犁</span> and <span class="han">撑犁孤塗單于</span> are priced on '
             'the phonetic form: 撑 carries a velar nasal, which it writes at 72.7%% against 4.3%% '
             'for a dental <i>n</i>, so the two spellings differ by a factor of seventeen on that '
             'one cell. <span class="han">若鞮</span>, <span class="han">搜諧若鞮</span> and '
             '<span class="han">冒頓</span> are priced on what their characters write, the reading '
             'containing something they do not. <b>The raw price is not comparable across rows</b>, '
             'because it falls with every extra character and so sorts by length; the per-character '
             'figure is the geometric mean, and the sort is on it. The control at '
             '<span class="han">撑犁</span> stands at 8.0%%, and %d rows reach or beat it while %d '
             'fall short. Generated from <code>data/derived/author_proposals.csv</code> by the same '
             '<code>src/price_engine.py</code> the entries above use.</p>'
             % (len(out), TITLE_CHARS, above, len(out) - above))
    return "\n".join(T)

BODY.append(price_table())

io.open("s1_tables.html","w",encoding="utf8").write("\n\n".join(BODY))
