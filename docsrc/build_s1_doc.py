import io, re
head=io.open("_s1_head.html",encoding="utf8").read()
top=io.open("s1_prose_top.html",encoding="utf8").read()
tab=io.open("s1_tables.html",encoding="utf8").read()
bot=io.open("s1_prose_bottom.html",encoding="utf8").read()
i=head.index("</style>")+len("</style>")
HEAD=('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
      '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
      '<title>Supplementary S1: Candidate Readings</title>\n')
full=HEAD+head[:i]+"\n</head>\n<body>\n"+head[i:].lstrip("\n")+"\n"+top+"\n"+tab+"\n"+bot+"\n</body>\n</html>\n"
io.open("supplementary_S1_full.html","w",encoding="utf8").write(full)
io.open("supplementary_S1_candidate_readings.html","w",encoding="utf8").write(full)
dx=re.sub(r'(<span class="n">[^<]*</span>)(<span class="t">)', r'\1 \2', full)
io.open("supplementary_S1_full_dx.html","w",encoding="utf8").write(dx)
print("wrote", len(full))
