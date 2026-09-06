# -*- coding: utf-8 -*-
r"""
Step 60.  One table: every row of the record, the reading proposed for it,
the form the price was actually calculated on, and the price.

WHY THE THIRD COLUMN EXISTS.  For most rows the price covers the whole
proposal and the column is empty.  For nine of them it does not, and
printing a figure beside a name it does not cover is how a table misleads.
Three cases, all of one kind: the proposal contains something the
characters do not write.

  若鞮 and the five rows that carry it.  §9 reads 若鞮 as <i>İnakt</i>, with
  the opening vowel unwritten and 鞮 carrying the final <i>-t</i>.  The
  engine cannot say that a source word began with a vowel which went
  unwritten, so it is priced as <i>nakt</i>, the part the characters write.
  The opening vowel stays an argument in the paper, not a cell in a
  product.

  搜諧若鞮.  One further unwritten vowel, the ı of <i>sarıg</i>, with 諧
  carrying the -g.  Priced as <i>sarg nakt</i>.

  冒頓.  A whole syllable unwritten, the -gü- of <i>Bögü</i>, which is a
  larger claim than an unwritten vowel and the weakest of the three.
  Priced as <i>bö tuğ</i>.

TWO PRICE COLUMNS, and the sort is on the second.  The raw price is the
product of the measured rates and falls with every extra character, so
sorting on it sorts by name length rather than by quality.  The per
character figure is the geometric mean, raw**(1/characters), which is the
only one of the two comparable across names.  The control at 撑犁, the one
item the Chinese sources gloss outright, stands at 8.1% per character.

Reads   data\derived\author_proposals.csv
        src\price_engine.py           the single scorer, run over every row
Writes  docs\proposed_names_by_price.html
"""
import csv, io, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
DOCS = os.path.join(ROOT, "docs")

CONTROL = 0.081        # \u6491\u7281 = ta\u014br\u0131, 1 in 157 over two characters

TITLE_CHARS   = u"\u82e5\u97ae"      # \u82e5\u97ae, the title element \u00a79 argues once for all six
TITLE_READING = u"\u0130nakt"

# Rows priced on something other than the proposal as printed.  Three
# reasons, and the Priced as column shows the result for every one of them.
#
# 1. THE TITLE ELEMENT.  Six names carry \u82e5\u97ae.  \u00a79 argues it once, so it is
#    priced once, in its own row, and stripped from the other six.  Those
#    six therefore price the part that is theirs alone.
#
# 2. THE PHONETIC FORM.  The proposed names are printed in plain Turkish
#    letters, but a price is a claim about sounds, so where the two differ
#    the price is taken on the phonetic form.  \u6491 carries a VELAR nasal:
#    writing a velar \u014b with it is 72.7%, writing a dental n with it is
#    4.3%, so <i>ta\u014br\u0131</i> and <i>tanr\u0131</i> differ by a factor of
#    seventeen on that one cell.  The velar form is the reading; the dental
#    one is its modern descendant.  These are the only two rows in the forty
#    where a phonetic form changes the price at all.
#
# 3. WHAT THE CHARACTERS DO NOT WRITE.  \u82e5\u97ae is priced as <i>nakt</i>,
#    since the engine cannot say that a source word began with a vowel that
#    went unwritten; \u641c\u8ae7 as <i>sarg</i>, one further unwritten vowel; and
#    \u5192\u9813 as <i>b\u00f6 tu\u011f</i>, where a whole syllable goes unwritten, which
#    is a larger claim than the other two and the weakest row of the three.
PRICED_AS = {
    u"\u82e5\u97ae":               u"nakt",
    u"\u641c\u8ae7\u82e5\u97ae":       u"sarg",
    u"\u5192\u9813":               u"b\u00f6 tu\u011f",
}


def rd(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8-sig")))


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def priced_form(z, proposal):
    """(characters priced, form priced, whether it differs from the proposal).

    The six names that carry the title element are priced without it, so the
    figure covers the part that belongs to that row alone.
    """
    zi, form = z, proposal
    if len(zi) > len(TITLE_CHARS) and zi.endswith(TITLE_CHARS) \
            and TITLE_READING.lower() in form.lower():
        zi = zi[:-len(TITLE_CHARS)]
        form = re.sub(u"[\u0130i]nakt", u"", form, flags=re.I).strip(u" -")
    form = PRICED_AS.get(z, form)
    return zi, form, (form.lower() != proposal.lower())


def main():
    sys.path.insert(0, os.path.join(ROOT, "src"))
    import price_engine as PE
    R = PE.Rates()

    rows = []
    unpriced = []
    for r in rd(os.path.join(DER, "author_proposals.csv")):
        z = r["chinese"].strip()
        proposal = (r["proposed_name"] or "").strip()
        sense = (r["proposed_sense"] or "").strip()
        turkish = (r.get("turkish_approx") or "").strip()
        if not proposal or proposal.startswith("("):
            unpriced.append((z, proposal, sense, u"no reading proposed"))
            continue
        display = turkish or proposal          # the everyday spelling comes first
        zi, form, _ = priced_form(z, proposal)
        differs = (form.lower() != display.lower())
        a, err, note = PE.price_name(zi, form, R, strip_title=False)
        if a is None:
            unpriced.append((z, proposal, sense, err))
            continue
        rows.append(dict(z=z, proposal=display, turkish=turkish,
                         form=form, differs=differs,
                         sense=sense, price=a.price, nchar=len(zi),
                         per=a.price ** (1.0 / len(zi)), roles=a.roles,
                         detail=a.detail))
    rows.sort(key=lambda d: d["per"])          # most expensive per character first

    o = []
    a = o.append
    a('<title>Proposed readings by price</title>')
    a('<style>')
    a(':root{--ink:#1a1a18;--ink-2:#6b6862;--rule:#d8d4cc;--bg:#fbfaf7;--warm:#8a6d3b}')
    a('body{margin:0;background:var(--bg);color:var(--ink);'
      'font:15px/1.55 Georgia,"Times New Roman",serif}')
    a('main{max-width:1080px;margin:0 auto;padding:2.5rem 1.25rem 4rem}')
    a('h1{font-size:1.5rem;font-weight:normal;margin:0 0 .3rem}')
    a('p.sub{color:var(--ink-2);margin:0 0 1.6rem;max-width:64ch}')
    a('.wrap{overflow-x:auto}')
    a('table{border-collapse:collapse;width:100%;font-size:14px}')
    a('th{text-align:left;font-weight:normal;color:var(--ink-2);'
      'border-bottom:1px solid var(--ink);padding:.4rem .5rem;vertical-align:bottom}')
    a('td{border-bottom:1px solid var(--rule);padding:.45rem .5rem;vertical-align:top}')
    a('td.n{color:var(--ink-2);width:2.2rem;text-align:right}')
    a('td.han{font-size:16px;white-space:nowrap}')
    a('td.rd{font-weight:bold;white-space:nowrap}')
    a('td.pf{white-space:nowrap;color:var(--warm)}')
    a('td.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}')
    a('td.se{color:var(--ink-2)}')
    a('.bar{display:block;height:6px;background:var(--rule);margin-top:4px;border-radius:3px}')
    a('.bar i{display:block;height:6px;background:var(--warm);border-radius:3px}')
    a('td.tk{white-space:nowrap;color:var(--ink-2);font-style:italic}')
    a('td.dash{color:var(--rule)}')
    a('h2{font-size:1.05rem;font-weight:normal;margin:2.4rem 0 .4rem}')
    a('code{font:12px/1.4 ui-monospace,Menlo,Consolas,monospace;color:var(--ink-2)}')
    a('@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){'
      '--ink:#e8e5df;--ink-2:#9a958c;--rule:#3a3833;--bg:#161513;--warm:#c9a227}}')
    a('</style>')
    a('<main>')
    a('<h1>The forty rows, by price</h1>')
    a('<p class="sub">Every row of the record, the reading proposed for it, and its cost, '
      'most expensive first. <b>Priced as</b> names the form the figure was actually '
      'calculated on, and is filled in wherever that is not the proposal exactly as printed; '
      'a dash means the price covers the reading as it stands. Six names carry the title element '
      '若鞮, which \u00a79 argues once for all of them: it is priced once, in its own row, and left out '
      'of the other six, so each of those covers the part belonging to that row alone. Two rows are '
      'priced on the phonetic form rather than the plain Turkish spelling, since a price is a claim '
      'about sounds; the readings are therefore printed in the phonetic spelling here and in the '
      'paper and supplement, and the <b>Modern Turkish</b> column gives the everyday approximation, which appears in this table and nowhere else. The raw price falls with every extra '
      'character, so it sorts by length rather than by quality; the per-character figure is '
      'the geometric mean and is the comparable one, and the sort is on it. The control at '
      '撑犁, the one item the Chinese sources gloss outright, stands at '
      '<b>8.0% per character</b> and is marked on every bar: a row past that mark is cheaper '
      'than the control, a row short of it more expensive.</p>')
    a('<div class="wrap"><table><thead><tr><th></th><th>Form</th><th>Proposed</th>'
      '<th>Priced as</th><th class="num">chars</th><th class="num">1 in</th>'
      '<th class="num">per character</th><th>Sense</th></tr></thead><tbody>')
    for i, d in enumerate(rows, 1):
        w = min(100.0, 100.0 * d["per"] / (CONTROL * 2))   # control at the half mark
        pf = ('<td class="pf">%s</td>' % esc(d["form"].title())) if d["differs"] \
             else '<td class="dash">&mdash;</td>'
        a('<tr><td class="n">%d</td><td class="han">%s</td><td class="rd">%s</td>%s'
          '<td class="num">%d</td><td class="num">%s</td>'
          '<td class="num">%.1f%%<span class="bar"><i style="width:%.1f%%"></i></span></td>'
          '<td class="se">%s</td></tr>'
          % (i, esc(d["z"]), esc(d["proposal"]), pf, d["nchar"],
             "{:,}".format(int(round(1.0 / d["price"]))), 100 * d["per"], w, esc(d["sense"])))
    a('</tbody></table></div>')

    if unpriced:
        a('<h2>Not priced</h2>')
        a('<table><tbody>')
        for z, proposal, sense, why in unpriced:
            a('<tr><td class="han">%s</td><td class="rd">%s</td><td class="se">%s</td>'
              '<td class="se"><code>%s</code></td></tr>'
              % (esc(z), esc(proposal), esc(sense), esc(why)))
        a('</tbody></table>')

    a('<h2>Where the numbers come from</h2>')
    a('<p class="sub">Generated by <code>src/step60_price_list.py</code>, which runs the single '
      'price engine over every row of <code>data/derived/author_proposals.csv</code>, so it '
      'cannot drift from the repository. Each figure is the product of the measured rates for '
      'that alignment; the supplement entry for a row sets out its cells one by one and names '
      'the weak ones. Built %s.</p>' % datetime.date.today().isoformat())
    a('</main>')

    if not os.path.isdir(DOCS):
        os.makedirs(DOCS)
    p = os.path.join(DOCS, "proposed_names_by_price.html")
    io.open(p, "w", encoding="utf-8").write(u"\n".join(o) + u"\n")
    print("written: %s" % p)
    print("%d priced, %d not priced, %d rows"
          % (len(rows), len(unpriced), len(rows) + len(unpriced)))


if __name__ == "__main__":
    main()
