# -*- coding: utf-8 -*-
"""
sort_resources.py
=================
Files my_resources/ into:

    my_resources/lexicons/   source texts the extraction scripts parse
    References/              scholarship that is cited but not parsed

Written in Python rather than batch because the filenames carry non-ASCII
characters (’ ı İ æ) that cmd handles badly, and because when a move fails
this reports why.

Nothing is deleted. Safe to run repeatedly.
"""
import glob, os, shutil, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
RES  = os.path.join(ROOT, "my_resources")
LEX  = os.path.join(RES, "lexicons")
REFS = os.path.join(ROOT, "References")

print()
print("  root      : %s" % ROOT)
print("  resources : %s" % RES)
print()
if not os.path.isdir(RES):
    print("  [STOP] no my_resources folder there"); sys.exit(1)
for d in (LEX, REFS):
    os.makedirs(d, exist_ok=True)

PLAN = [
    ("Divanu-Lugatit-Turk-Dizini*.pdf",   LEX,  "Divanu-Lugatit-Turk-Dizini-2MB.pdf"),
    ("Codex cumanicus Bibliothec*.zip",   LEX,  "Codex_Cumanicus_Kuun_1880.zip"),
    ("Sir Gerard Clauson*.epub",          LEX,  "Clauson_1972_EDPT.epub"),
    ("kitbalidrkllisna*.epub",            LEX,  "AbuHayyan_Kitab_al-Idrak.epub"),
    ("Kutadgu Bilig Ciltli*.pdf",         LEX,  "Kutadgu_Bilig_Kabalci_2008.pdf"),
    ("KUTAGU BILIG*.epub",                LEX,  "Kutadgu_Bilig_TDV_2018.epub"),
    ("Kutadgu Bilig Incelemesi*.pdf",     LEX,  "Kutadgu_Bilig_Incelemesi_Dilacar.pdf"),
    ("Codex Cumanicus",                   LEX,  "Codex_Cumanicus_facsimile"),
    ("jesh-article-p121*.pdf",            REFS, "Esin_OSullivan_2025_Xiongnu_rulers_residences.pdf"),
    ("Pulleyblank - Hun Language*.html",  REFS, "Pulleyblank_Hun_Language_TurkicWorld.html"),
    ("Pulleyblank - Hun Language - TurkicWorld_files", REFS,
                                                "Pulleyblank_Hun_Language_TurkicWorld_files"),
]

moved = skipped = missing = failed = 0
for pattern, dest_dir, new_name in PLAN:
    dest = os.path.join(dest_dir, new_name)
    if os.path.exists(dest):
        print("  [skip ] %s already filed" % new_name); skipped += 1; continue
    hits = glob.glob(os.path.join(RES, pattern))
    hits = [h for h in hits if os.path.basename(h) != "lexicons"]
    if not hits:
        print("  [none ] nothing matches %s" % pattern); missing += 1; continue
    if len(hits) > 1:
        print("  [FAIL ] %s matches %d files, not moving:" % (pattern, len(hits)))
        for h in hits: print("            %s" % os.path.basename(h))
        failed += 1; continue
    try:
        shutil.move(hits[0], dest)
        print("  [moved] %s" % new_name); moved += 1
    except Exception as e:
        print("  [FAIL ] %s" % new_name)
        print("            %s: %s" % (type(e).__name__, e)); failed += 1

print()
print("  moved %d | already filed %d | not found %d | failed %d"
      % (moved, skipped, missing, failed))
print()
print("  my_resources/lexicons/ :")
for n in sorted(os.listdir(LEX)): print("     %s" % n)
loose = [n for n in sorted(os.listdir(RES)) if n != "lexicons"]
print()
print("  still loose in my_resources/ :")
for n in loose: print("     %s" % n)
if not loose: print("     (nothing)")
print()
print("  Nothing was deleted.")
