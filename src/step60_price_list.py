# -*- coding: utf-8 -*-
r"""
Step 60.  One page listing every proposed reading with its meaning and its
price, sorted from the most expensive to the cheapest.

TWO PRICE COLUMNS, and the sort is on the second.  The RAW figure is the
product of the measured rates and falls with every extra character, so
sorting on it sorts mostly by name length: an eight-character name is dear
because it is long, not because the reading is bad.  The PER CHARACTER
figure is the geometric mean, raw**(1/characters), and is the only one of
the two that can be compared across names.  The control at 撑犁 sits at
8.1% per character, and it is drawn on the page so that each row can be
read against it.

Reads   data\derived\name_prices.csv     written by step 57
        data\derived\author_proposals.csv
Writes  docs\proposed_names_by_price.html
"""
import csv, io, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NAMES_ROOT") or os.path.dirname(HERE)
DER  = os.path.join(ROOT, "data", "derived")
DOCS = os.path.join(ROOT, "docs")

CONTROL = 0.081          # 撑犁 = taŋrı, 1 in 152 over two characters

def rd(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8-sig")))

def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def main():
    pr = rd(os.path.join(DER, "name_prices.csv"))
    ap = {r["chinese"]: r for r in rd(os.path.join(DER, "author_proposals.csv"))}
    ok, blocked = [], []
    for r in pr:
        z = r["chinese"]
        sense = (ap.get(z, {}).get("proposed_sense") or "").strip()
        if r["one_in"] and r["one_in"] not in ("", "0"):
            ok.append((float(r["per_char"]), int(r["one_in"]), z, r["reading"],
                       sense, int(r["n_chars"]), r["alignment"]))
        else:
            blocked.append((z, r["reading"], sense, r["note"]))
    ok.sort()                                    # dearest per character first

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
    a('<p class="sub">Every proposed reading with its sense and its cost, dearest first. '
      'The raw price falls with every extra character, so it sorts by length rather than by '
      'quality; the per-character figure is the geometric mean and is the comparable one, and '
      'the sort is on it. The control at 撑犁, the one item the Chinese sources gloss '
      'outright, stands at <b>8.1% per character</b>, marked on every bar. A row above that line '
      'is cheaper than the control, a row below it dearer.</p>')
    a('<table><thead><tr><th></th><th>Form</th><th>Reading</th>'
      '<th class="num">1 in</th><th class="num">per character</th><th>Sense</th></tr></thead><tbody>')
    for i, (pc, oi, z, reading, sense, nc, align) in enumerate(ok, 1):
        w = min(100.0, 100.0 * pc / (CONTROL * 2))     # control sits at the half mark
        cls = ' class="over"' if pc >= CONTROL else ''
        a('<tr%s><td class="n">%d</td><td class="han">%s</td><td class="rd">%s</td>'
          '<td class="num">%s</td><td class="num pc">%.1f%%<span class="bar">'
          '<i style="width:%.1f%%"></i></span></td><td class="se">%s</td></tr>'
          % (cls, i, esc(z), esc(reading), "{:,}".format(oi), 100 * pc, w, esc(sense)))
    a('</tbody></table>')
    if blocked:
        a('<h2>Not priced</h2>')
        a('<p class="sub">These are blocked by a measured zero or by a cell the corpus never '
          'tested, not by an oversight in the engine. A zero has no rate to multiply.</p>')
        a('<table><tbody>')
        for z, reading, sense, note in blocked:
            a('<tr><td class="han">%s</td><td class="rd">%s</td><td class="se">%s</td>'
              '<td class="se"><code>%s</code></td></tr>'
              % (esc(z), esc(reading), esc(sense), esc(note)))
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
    print("%d priced, %d blocked, %d rows" % (len(ok), len(blocked), len(ok) + len(blocked)))

if __name__ == "__main__":
    main()
