# -*- coding: utf-8 -*-
r"""
Step 60.  One page listing every proposed reading with its meaning and its
price, sorted from the most expensive to the cheapest.

TWO PRICE COLUMNS, and the sort is on the second.  The RAW figure is the
product of the measured rates and falls with every extra character, so
sorting on it sorts mostly by name length: an eight-character name is expensive
because it is long, not because the reading is bad.  The PER CHARACTER
figure is the geometric mean, raw**(1/characters), and is the only one of
the two that can be compared across names.  The control at 撑犁 sits at
8.1% per character, and it is drawn on the page so that each row can be
read against it.

Reads   data\derived\name_prices.csv     written by step 57
        data\derived\author_proposals.csv
Writes  docs\proposed_names_by_price.html
"""
import csv, io, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
DOCS = os.path.join(ROOT, "docs")

CONTROL = 0.081          # 撑犁 = taŋrı, 1 in 152 over two characters

def rd(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8-sig")))

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

TITLE_CHARS = u"\u82e5\u97ae"          # \u82e5\u97ae, argued once in \u00a79 and not priced again
TITLE_READING = u"\u0130nakt"

# Three rows cannot be priced as proposed, because the proposal contains
# something the characters do not write.  The same situation as \u82e5\u97ae, where
# \u00a79 reads <i>\u0130nakt</i> and the characters write <i>nakt</i>.  For each one the
# written form is named here and priced instead, so that the row carries a
# figure and the unwritten part stays a separate claim rather than a blocking
# zero.  What is unwritten differs in weight and the page says so:
#   \u641c\u8ae7\u82e5\u97ae  one vowel, the \u0131 of sar\u0131g, with \u8ae7 carrying the -g.  Exactly
#            the \u82e5\u97ae case, and the lightest of the three.
#   \u5192\u9813   a whole syllable, the -g\u00fc- of B\u00f6g\u00fc, which is a larger claim than
#            an unwritten vowel and is the weakest of the three.
SHORT = {
    u"\u641c\u8ae7\u82e5\u97ae": (u"sarg nakt", u"one unwritten vowel, and \u82e5\u97ae as nakt"),
    u"\u5192\u9813":   (u"b\u00f6 tu\u011f", u"the -g\u00fc- of B\u00f6g\u00fc unwritten"),
}


def short_price(z):
    """Price the written form of a row the proposal cannot express."""
    if z not in SHORT:
        return None
    sys.path.insert(0, os.path.join(ROOT, "src"))
    import price_engine as PE
    rd, why = SHORT[z]
    a, err, note = PE.price_name(z, rd, PE.Rates(), strip_title=False)
    if a is None:
        return None
    return rd, why, a.price, a.price ** (1.0 / len(z)), a.detail


def element_price():
    """The price of the title element \u82e5\u97ae, as the two characters write it.

    \u00a79 reads \u82e5\u97ae as <i>\u0130nakt</i>, with the opening vowel unwritten and \u97ae
    carrying the final <i>-t</i>.  The engine has no way to say that a source
    word began with a vowel which went unwritten, so asking it for <i>inakt</i>
    makes it put a bare <i>i</i> on \u82e5 and the whole of <i>nakt</i> on \u97ae, which
    prices a different alignment and returns a figure in the hundreds of
    millions.  Asking it for <i>nakt</i>, the part the characters actually
    write, gives the alignment \u00a79 argues: \u82e5 = <i>nakt</i>, \u97ae carrying the
    <i>-t</i>, 1 in 2,217.  That is the figure used here, and the opening vowel
    stays a separate question argued in the paper rather than a cell in a
    product.
    """
    sys.path.insert(0, os.path.join(ROOT, "src"))
    import price_engine as PE
    a, err, note = PE.price_name(TITLE_CHARS, u"nakt", PE.Rates(), strip_title=False)
    if a is None:
        raise SystemExit("could not price the title element: %s" % err)
    return a.price, a.detail


def priced_scope(z, reading, note):
    """What the figure on this row actually covers.

    Five rows carry the title element \u82e5\u97ae, and the engine strips it before
    pricing, because \u00a79 argues it once for all of them.  So the price beside
    <i>Ulu\u011f \u0130nakt</i> is the price of <i>Ulu\u011f</i> on \u70cf\u7d2f, not of the whole
    four-character form.  Printing the full form and reading beside a figure
    that covers less than either invites exactly the wrong reading of the
    table, so the narrower scope is printed with it.
    """
    if z == TITLE_CHARS:
        return TITLE_CHARS, u"nakt"
    if u"title element" not in (note or u""):
        return None
    form = z[:-len(TITLE_CHARS)]
    rd = reading.replace(TITLE_READING, u"").strip(u" -")
    return form, rd


BARE = re.compile(u"(\\S+)=([aeiou\u0131\u00f6\u00fc\u0251]\\S*)")

def bare_vowel(alignment):
    """True when some character is made to write a syllable with no onset and
    is not a glottal character, which is the one licensed vehicle for that.

    The engine has no way to say that the SOURCE word began with a vowel that
    went unwritten.  Where a reading needs that, the aligner has to put the
    bare vowel on a character instead, and the price it returns is not the
    price of the reading that was argued.  \u82e5\u97ae is the case: \u00a79 reads \u82e5 as
    <i>nak</i> with the opening vowel unwritten and \u97ae carrying the final
    <i>-t</i>, and the aligner instead puts <i>i</i> on \u82e5 and the whole of
    <i>nakt</i> on \u97ae.  Such rows are listed apart rather than sorted in,
    because their figure would otherwise head the table and be read as the
    most expensive reading in the file when it is the one the engine cannot state.
    """
    for m in BARE.finditer(alignment or ""):
        if not m.group(1).startswith(u"\u0294"):
            return True
    return False


def main():
    EL, EL_DETAIL = element_price()
    pr = rd(os.path.join(DER, "name_prices.csv"))
    ap = {r["chinese"]: r for r in rd(os.path.join(DER, "author_proposals.csv"))}
    ok, blocked, unexpressed = [], [], []
    for r in pr:
        z = r["chinese"]
        sense = (ap.get(z, {}).get("proposed_sense") or "").strip()
        if z == TITLE_CHARS:
            # Step 57 asks the engine for the whole reading, inakt, and gets the
            # alignment it cannot state; use the element price computed above,
            # which is the alignment \u00a79 argues.  Without this the row heads the
            # table at 1 in 232 million and looks like the worst reading in the
            # file when it is the one the engine has no way to express.
            r = dict(r, price="%.12f" % EL, one_in=str(int(round(1.0 / EL))),
                     per_char="%.8f" % (EL ** 0.5), n_chars="2",
                     alignment=EL_DETAIL, note=u"priced as nakt, the part the "
                     u"characters write; the opening vowel is argued in \u00a79")
        if not (r["one_in"] and r["one_in"] not in ("", "0")):
            blocked.append((z, r["reading"], sense, r["note"]))
        elif bare_vowel(r["alignment"]):
            unexpressed.append((float(r["per_char"]), int(r["one_in"]), z,
                                r["reading"], sense, r["alignment"]))
        else:
            ok.append((float(r["per_char"]), int(r["one_in"]), z, r["reading"],
                       sense, int(r["n_chars"]), r["alignment"],
                       priced_scope(z, r["reading"], r["note"]),
                       (float(r["price"]) * EL, int(r["n_chars"]) + len(TITLE_CHARS))
                       if u"title element" in (r["note"] or u"") else None))
    ok.sort()                                    # most expensive per character first
    unexpressed.sort()

    o = []
    a = o.append
    a('<title>Proposed readings by price</title>')
    a('<style>')
    a(':root{--ink:#1a1a18;--ink-2:#6b6862;--rule:#d8d4cc;--bg:#fbfaf7;--warm:#8a6d3b}')
    a('body{margin:0;background:var(--bg);color:var(--ink);'
      'font:15px/1.55 Georgia,"Times New Roman",serif}')
    a('main{max-width:1000px;margin:0 auto;padding:2.5rem 1.25rem 4rem}')
    a('h1{font-size:1.5rem;font-weight:normal;margin:0 0 .3rem}')
    a('p.sub{color:var(--ink-2);margin:0 0 1.6rem;max-width:62ch}')
    a('table{border-collapse:collapse;width:100%;font-size:14px}')
    a('th{text-align:left;font-weight:normal;color:var(--ink-2);'
      'border-bottom:1px solid var(--ink);padding:.4rem .5rem;vertical-align:bottom}')
    a('td{border-bottom:1px solid var(--rule);padding:.45rem .5rem;vertical-align:top}')
    a('td.n{color:var(--ink-2);width:2.2rem;text-align:right}')
    a('td.han{font-size:16px;white-space:nowrap}')
    a('td.rd{font-weight:bold;white-space:nowrap}')
    a('td.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}')
    a('td.se{color:var(--ink-2)}')
    a('.sc{display:block;font-size:11.5px;color:var(--ink-2);font-weight:normal;letter-spacing:.02em;margin-top:2px}')
    a('.bar{display:block;height:6px;background:var(--rule);margin-top:4px;border-radius:3px}')
    a('.bar i{display:block;height:6px;background:var(--warm);border-radius:3px}')
    a('tr.over td.num.pc{color:var(--warm)}')
    a('h2{font-size:1.05rem;font-weight:normal;margin:2.4rem 0 .4rem}')
    a('code{font:12px/1.4 ui-monospace,Menlo,Consolas,monospace;color:var(--ink-2)}')
    a('@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){'
      '--ink:#e8e5df;--ink-2:#9a958c;--rule:#3a3833;--bg:#161513;--warm:#c9a227}}')
    a('</style>')
    a('<main>')
    a('<h1>The forty rows, by price</h1>')
    a('<p class="sub">Every proposed reading with its sense and its cost, most expensive first. '
      'The raw price falls with every extra character, so it sorts by length rather than by '
      'quality; the per-character figure is the geometric mean and is the comparable one, and '
      'the sort is on it. The control at 撑犁, the one item the Chinese sources gloss '
      'outright, stands at <b>8.1% per character</b>, marked on every bar. A row above that line '
      'is cheaper than the control, a row below it more expensive. Five rows carry the title element \u82e5\u97ae, which \u00a79 argues once for all of them and the engine therefore strips before pricing; on those rows the figure covers only the part marked <i>priced</i>, not the whole form or the whole reading. The line marked <i>with \u82e5\u97ae</i> adds the element back in at 1 in 2,217, the price of <i>nakt</i>, which is what those two characters write; the opening vowel of <i>\u0130nakt</i> is unwritten and is argued in \u00a79 rather than priced here.</p>')
    a('<table><thead><tr><th></th><th>Form</th><th>Reading</th>'
      '<th class="num">1 in</th><th class="num">per character</th><th>Sense</th></tr></thead><tbody>')
    for i, (pc, oi, z, reading, sense, nc, align, scope, total) in enumerate(ok, 1):
        w = min(100.0, 100.0 * pc / (CONTROL * 2))     # control sits at the half mark
        cls = ' class="over"' if pc >= CONTROL else ''
        fcell, rcell = esc(z), esc(reading)
        pcell = "%.1f%%" % (100 * pc)
        if scope:
            fcell += '<span class="sc">priced: %s</span>' % esc(scope[0])
            rcell += '<span class="sc">priced: %s</span>' % esc(scope[1])
        if total:
            tp, tc = total
            pcell += ('<span class="sc">with %s: %.1f%%</span>'
                      % (esc(TITLE_CHARS), 100 * tp ** (1.0 / tc)))
            ocell = ("{:,}".format(oi)
                     + '<span class="sc">with %s: %s</span>'
                     % (esc(TITLE_CHARS), "{:,}".format(int(round(1.0 / tp)))))
        else:
            ocell = "{:,}".format(oi)
        a('<tr%s><td class="n">%d</td><td class="han">%s</td><td class="rd">%s</td>'
          '<td class="num">%s</td><td class="num pc">%s<span class="bar">'
          '<i style="width:%.1f%%"></i></span></td><td class="se">%s</td></tr>'
          % (cls, i, fcell, rcell, ocell, pcell, w, esc(sense)))
    a('</tbody></table>')
    if unexpressed:
        a('<h2>One reading the engine cannot state</h2>')
        a('<p class="sub">The price engine has no way to say that the source word '
          'began with a vowel which went unwritten. Where a reading needs that, the aligner '
          'has to put a bare vowel on a character instead, and the figure it returns prices a '
          'different alignment from the one that was argued. These rows are set apart rather '
          'than sorted in, because the figure would otherwise head the table and be read as the '
          'most expensive reading in the file when it is the one the engine cannot express.</p>')
        a('<table><tbody>')
        for pc, oi, z, reading, sense, align in unexpressed:
            a('<tr><td class="han">%s</td><td class="rd">%s</td>'
              '<td class="num">%s</td><td class="num">%.3f%%</td><td class="se">%s</td></tr>'
              % (esc(z), esc(reading), "{:,}".format(oi), 100 * pc, esc(sense)))
            a('<tr><td></td><td colspan="4" class="se"><code>%s</code></td></tr>' % esc(align))
        a('</tbody></table>')
    if blocked:
        a('<h2>Priced as the characters write them</h2>')
        a('<p class="sub">These three cannot be priced as proposed, because each proposal '
          'contains something the characters do not write, and a zero has no rate to multiply. '
          'They are priced here on the written form instead, the same move as \u82e5\u97ae, where '
          '\u00a79 reads <i>\u0130nakt</i> and the two characters write <i>nakt</i>. The unwritten part '
          'then stays a separate claim rather than a blocking zero, and its weight differs from '
          'row to row.</p>')
        a('<table><thead><tr><th>Form</th><th>Proposed</th><th>Written form</th>'
          '<th class="num">1 in</th><th class="num">per character</th><th>What is unwritten</th>'
          '</tr></thead><tbody>')
        for z, reading, sense, note in blocked:
            sp = short_price(z)
            if sp:
                wform, why, pv, pc, detail = sp
                a('<tr><td class="han">%s</td><td class="rd">%s</td><td class="rd">%s</td>'
                  '<td class="num">%s</td><td class="num pc">%.1f%%</td><td class="se">%s</td></tr>'
                  % (esc(z), esc(reading), esc(wform.title()),
                     "{:,}".format(int(round(1.0 / pv))), 100 * pc, esc(why)))
                a('<tr><td></td><td colspan="5" class="se"><code>%s</code></td></tr>' % esc(detail))
            else:
                a('<tr><td class="han">%s</td><td class="rd">%s</td><td class="se" colspan="4">'
                  '%s</td></tr>' % (esc(z), esc(reading), esc(note)))
        a('</tbody></table>')
    a('<h2>Where the numbers come from</h2>')
    a('<p class="sub">Generated by <code>src/step60_price_list.py</code> from '
      '<code>data/derived/name_prices.csv</code>, which step 57 writes by running the single '
      'price engine over all forty rows, and from <code>data/derived/author_proposals.csv</code>. '
      'It cannot drift from the repository. Built %s.</p>'
      % datetime.date.today().isoformat())
    a('</main>')

    if not os.path.isdir(DOCS):
        os.makedirs(DOCS)
    p = os.path.join(DOCS, "proposed_names_by_price.html")
    io.open(p, "w", encoding="utf-8").write(u"\n".join(o) + u"\n")
    print("written: %s" % p)
    print("%d priced, %d not expressible, %d blocked, %d rows"
          % (len(ok), len(unexpressed), len(blocked),
             len(ok) + len(unexpressed) + len(blocked)))

if __name__ == "__main__":
    main()
