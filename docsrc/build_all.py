# -*- coding: utf-8 -*-
r"""Run the whole document chain, and stop at the first step that fails.

This exists because a step once failed with a SyntaxError in s1_rows.py, the
later steps ran anyway on the stale intermediate, and build_docs.py's manifest
then reported "all current" because the outputs it checked had just been
rewritten with fresh timestamps. A freshness check cannot see a step that never
produced anything. Run this rather than the four scripts by hand.
"""
import subprocess, sys

CHAIN = ["build_paper.py", "build_s1.py", "build_s1_doc.py", "build_docs.py"]

for step in CHAIN:
    r = subprocess.run([sys.executable, step], capture_output=True)
    out = r.stdout.decode("utf8", "replace")
    err = r.stderr.decode("utf8", "replace")
    if r.returncode != 0:
        sys.stderr.write("\n*** %s FAILED, chain stopped. Nothing downstream was run,\n"
                         "*** so docs\\ still holds the PREVIOUS build. Do not ship.\n\n" % step)
        sys.stderr.write(err[-3000:] + "\n")
        sys.exit(1)
    if err.strip():
        sys.stderr.write("%s wrote to stderr:\n%s\n" % (step, err[-1500:]))
    print(out.rstrip())
