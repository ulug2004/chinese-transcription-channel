import sys, io, re, asyncio, os
from playwright.async_api import async_playwright

src, out, running = sys.argv[1], sys.argv[2], sys.argv[3]
s = io.open(src, encoding="utf8").read()
css = io.open("print.css", encoding="utf8").read()
inj = "<style>\n" + css + "\n</style>"
if "</head>" in s:
    s = s.replace("</head>", inj + "\n</head>")
else:
    s = inj + s
    s = '<!doctype html><html lang="en"><head><meta charset="utf-8">' + inj + '</head><body>' + io.open(src,encoding="utf8").read() + '</body></html>'
tmp = out + ".tmp.html"
io.open(tmp, "w", encoding="utf8").write(s)

HDR = ('<div style="font-family:Georgia,serif;font-size:7.5pt;color:#666;width:100%;'
       'padding:0 18mm;display:flex;justify-content:space-between;">'
       '<span>' + running + '</span><span>Uluğ &middot; 2026</span></div>')
FTR = ('<div style="font-family:Georgia,serif;font-size:7.5pt;color:#666;width:100%;'
       'padding:0 18mm;text-align:center;">'
       '<span class="pageNumber"></span> / <span class="totalPages"></span></div>')

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        await pg.emulate_media(media="print", color_scheme="light")
        await pg.goto("file://" + os.path.abspath(tmp), wait_until="networkidle")
        await pg.pdf(path=out, format="A4", print_background=True,
                     display_header_footer=True,
                     header_template=HDR, footer_template=FTR,
                     margin={"top":"22mm","bottom":"18mm","left":"18mm","right":"18mm"})
        await b.close()
asyncio.run(main())
print("wrote", out)
