# -*- coding: utf-8 -*-
"""Build the DOCX and PDF for both documents from the generated HTML."""
import io, os, re, subprocess, sys, glob, shutil

CHROME = None
for pat in ("/opt/pw-browsers/chromium*/chrome-linux/chrome",
            "/opt/pw-browsers/chromium*/chrome-linux*/headless_shell",
            "/opt/pw-browsers/chromium*/*/chrome"):
    hits = sorted(glob.glob(pat))
    if hits:
        CHROME = hits[-1]; break

PRINT = io.open("print.css", encoding="utf8").read()

JOBS = [("paper_full.html", "paper_full_dx.html", "paper_submission_jdmdh"),
        ("supplementary_S1_full.html", "supplementary_S1_full_dx.html",
         "supplementary_S1_candidate_readings")]

def pdf(src, out):
    s = io.open(src, encoding="utf8").read()
    s = s.replace("</head>", "<style>\n" + PRINT + "\n</style>\n</head>", 1)
    tmp = os.path.abspath("_print_" + os.path.basename(src))
    io.open(tmp, "w", encoding="utf8").write(s)
    if not CHROME:
        print("  no chromium found, PDF skipped"); return False
    cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", "--virtual-time-budget=20000",
           "--print-to-pdf=" + os.path.abspath(out), "file://" + tmp]
    r = subprocess.run(cmd, capture_output=True)
    ok = os.path.exists(out) and os.path.getsize(out) > 20000
    if not ok:
        sys.stderr.write(r.stderr.decode("utf8", "replace")[-1500:] + "\n")
    os.remove(tmp)
    return ok

for html, dxhtml, stem in JOBS:
    print(stem)
    r = subprocess.run(["pandoc", dxhtml, "-o", stem + ".docx"], capture_output=True)
    if r.returncode:
        sys.stderr.write(r.stderr.decode("utf8", "replace"))
    print("  docx", os.path.getsize(stem + ".docx") if os.path.exists(stem + ".docx") else "FAILED")
    if pdf(html, stem + ".pdf"):
        print("  pdf ", os.path.getsize(stem + ".pdf"))

# The author's hand-editable copies. These are committed to docs\edit\ on
# the author's machine, which the build never writes to. See docs/edit/README.md.
for src, dst in [("paper_submission_jdmdh.docx", "paper_EDIT.docx"),
                 ("supplementary_S1_candidate_readings.docx", "supplement_S1_EDIT.docx")]:
    if os.path.exists(src):
        shutil.copyfile(src, dst); print("refreshed", dst, "-> docs/edit/")

# Fingerprint what we are about to ship, so that next time we can tell an
# author edit from an untouched copy.  See check_edits.py, which must be run
# against the staged docs\edit\ BEFORE any rebuild: this overwrites the two
# files above, and a rebuild over an unread edit loses it silently.
try:
    import check_edits
    fp = check_edits.write_fingerprint(".")
    print("edit_fingerprint.json written for", len(fp), "file(s) -> docs/edit/")
except Exception as e:
    print("fingerprint FAILED:", e)

# ---------------------------------------------------------------- manifest
# The author reads the finished documents from docs\ after every build, so the
# build ends by stating exactly which files must reach docs\ and whether each
# one is younger than the source it was made from.  A build that leaves a stale
# file in docs\ is worse than a build that fails, because it looks finished.
# This list exists because docs\*.html was once left two builds behind while
# the PDF and DOCX beside it were current.
DOCS = [("paper_submission_jdmdh.html", "docs"),
        ("paper_submission_jdmdh.pdf", "docs"),
        ("paper_submission_jdmdh.docx", "docs"),
        ("supplementary_S1_candidate_readings.html", "docs"),
        ("supplementary_S1_candidate_readings.pdf", "docs"),
        ("supplementary_S1_candidate_readings.docx", "docs"),
        ("paper_EDIT.docx", "docs/edit"),
        ("supplement_S1_EDIT.docx", "docs/edit"),
        ("edit_fingerprint.json", "docs/edit")]
SOURCES = ["paper.html", "s1_rows.py", "s1_prose_top.html", "s1_prose_bottom.html"]

newest_src = max([os.path.getmtime(s) for s in SOURCES if os.path.exists(s)] or [0])
print("")
print("SHIP TO docs\\  (%d files, newest source %.0f)" % (len(DOCS), newest_src))
stale = 0
for name, dest in DOCS:
    if not os.path.exists(name):
        print("  MISSING  %-45s -> %s" % (name, dest)); stale += 1; continue
    age = os.path.getmtime(name)
    mark = "ok   " if age >= newest_src else "STALE"
    if mark == "STALE":
        stale += 1
    print("  %s %-45s -> %s  %d bytes" % (mark, name, dest, os.path.getsize(name)))
if stale:
    print("  %d file(s) missing or older than the sources. Do not ship." % stale)
else:
    print("  all current.")
