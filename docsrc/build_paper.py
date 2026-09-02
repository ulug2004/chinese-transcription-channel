import io, re, sys

frag = io.open("paper.html", encoding="utf8").read()

HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n')

# frag starts at <title> and ends with </style> ... body content
i = frag.index("</style>") + len("</style>")
head_part, body_part = frag[:i], frag[i:]

full = HEAD + head_part + "\n</head>\n<body>\n" + body_part.lstrip("\n") + "\n\n</body>\n</html>\n"
io.open("paper_full.html", "w", encoding="utf8").write(full)

# docx variant: space between section number and title so Word does not run them together
dx = re.sub(r'(<span class="n">[^<]*</span>)(<span class="t">)', r'\1 \2', full)
io.open("paper_full_dx.html", "w", encoding="utf8").write(dx)

io.open("paper_submission_jdmdh.html", "w", encoding="utf8").write(full)
print("paper_full.html", len(full), "| dx", len(dx))
