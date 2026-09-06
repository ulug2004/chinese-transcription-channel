# -*- coding: utf-8 -*-
r"""Before any rebuild: has the author edited docs\edit\ since we last shipped?

The two .docx files in docs\edit\ are the author's hand-editable copies, and
build_docs.py overwrites them at the end of every build.  That is safe only if
they still hold what we put there.  If the author has edited them, a rebuild
destroys the edits silently, which is the one failure this project cannot see
in a diff, because the masters are HTML and the edits are in Word.

Procedure, every time:

  1. stage docs\edit\paper_EDIT.docx, docs\edit\supplement_S1_EDIT.docx and
     docs\edit\edit_fingerprint.json out of the author's machine
  2. python check_edits.py <staged_dir>
  3. if it says EDITS PRESENT, fold them into docsrc\ first and only then build

build_docs.py writes edit_fingerprint.json beside the copies it makes, so the
fingerprint always describes the last version we shipped, not the last build.
"""
import hashlib, io, json, os, subprocess, sys

FILES = ["paper_EDIT.docx", "supplement_S1_EDIT.docx"]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_fingerprint(d="."):
    fp = {}
    for n in FILES:
        p = os.path.join(d, n)
        if os.path.exists(p):
            fp[n] = {"sha256": sha(p), "bytes": os.path.getsize(p)}
    io.open(os.path.join(d, "edit_fingerprint.json"), "w", encoding="utf8").write(
        json.dumps(fp, indent=2, sort_keys=True) + u"\n")
    return fp


def text(path):
    r = subprocess.run(["pandoc", path, "-t", "plain"], capture_output=True)
    return r.stdout.decode("utf8", "replace") if r.returncode == 0 else ""


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    fpath = os.path.join(d, "edit_fingerprint.json")
    if not os.path.exists(fpath):
        print("no edit_fingerprint.json in %s" % d)
        print("Cannot tell whether the author has edited. Ask before building.")
        return 2
    old = json.loads(io.open(fpath, encoding="utf8").read())
    changed = []
    for n in FILES:
        p = os.path.join(d, n)
        if not os.path.exists(p):
            print("  MISSING  %s" % n); continue
        now = sha(p)
        was = (old.get(n) or {}).get("sha256")
        if was is None:
            print("  no fingerprint on record for %s" % n); changed.append(n); continue
        if now == was:
            print("  unchanged  %s" % n)
        else:
            print("  EDITED     %s  (%s -> %s)" % (n, was[:12], now[:12]))
            changed.append(n)
    if not changed:
        print("\nNo author edits in docs\\edit\\. Safe to rebuild.")
        return 0
    print("\nAUTHOR EDITS PRESENT in %d file(s). Do NOT rebuild yet." % len(changed))
    print("Fold the wording into docsrc\\ first, then build, then reship the copies.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
