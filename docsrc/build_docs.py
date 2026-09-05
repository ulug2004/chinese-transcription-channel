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
