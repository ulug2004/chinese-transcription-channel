#!/usr/bin/env bash
# Downloads the freely-licensed datasets identified in references/corpus_audit.md
# into ../data/external/. Skips anything already present.
#
# Usage:  bash src/fetch_data.sh
#
# NOT downloaded here (see corpus_audit.md):
#   - Baxter-Sagart XLSX      : Dropbox link, no stated license — fetch manually and mirror
#   - UW Gaochang thesis PDF  : manual download, then extract appendix tables
#   - ytenx Zhengzhang data   : rights unclear, research use only — uncomment if appropriate
#   - Pulleyblank / Clauson / Lurje : print only, do not exist as data

set -uo pipefail
DEST="$(cd "$(dirname "$0")/.." && pwd)/data/external"
mkdir -p "$DEST"
cd "$DEST" || exit 1

get () {  # get <url> <outfile> <description>
  if [ -s "$2" ]; then printf '  [skip] %s\n' "$2"; return 0; fi
  printf '  [get ] %s — %s\n' "$2" "$3"
  if ! curl -fsSL --retry 3 --connect-timeout 20 -o "$2.part" "$1"; then
    printf '  [FAIL] %s (fetch manually: %s)\n' "$2" "$1"; rm -f "$2.part"; return 1
  fi
  mv "$2.part" "$2"
}

echo "=== 1. Schuessler — Later Han + Minimal Old Chinese (CC0) ==="
echo "    Zenodo record 14567004 — the Xiongnu-period phonological layer."
get "https://zenodo.org/records/14567004/files/LHantab.tsv?download=1" "LHantab.tsv" "Later Han Chinese"
get "https://zenodo.org/records/14567004/files/OCMtab.tsv?download=1" "OCMtab.tsv" "Minimal Old Chinese"

echo "=== 2. NTI / Fo Guang Shan Buddhist dictionary (CC BY-SA 3.0) ==="
echo "    Primary training corpus: ~9,688 Sanskrit-Chinese pairs."
NTI="https://raw.githubusercontent.com/alexamies/buddhist-dictionary/master/data/dictionary"
get "$NTI/buddhist_terminology.txt"   "buddhist_terminology.txt"   "18,215 entries"
get "$NTI/buddhist_named_entities.txt" "buddhist_named_entities.txt" "8,893 entries"

echo "=== 3. nk2028 tshet-uinh-data — Middle Chinese (CC0) ==="
NK="https://raw.githubusercontent.com/nk2028/tshet-uinh-data/main"
get "$NK/%E9%9F%BB%E6%9B%B8/%E5%BB%A3%E9%9F%BB.csv" "guangyun.csv" "廣韻, 25,336 rows"

echo "=== 4. Unihan (Unicode licence) ==="
echo "    kFanqie needs Unicode 16.0 or later."
get "https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip" "Unihan.zip" "Unihan database"

echo
echo "=== Manual steps remaining ==="
cat <<'NOTE'
  Baley Late Han v7 (CC BY 4.0) — the 401-item GOLD EVAL SET. Hold it out entirely.
      https://zenodo.org/records/14885154

  Baxter-Sagart OC v1.1 (no license stated) — mirror it, it lives on a personal Dropbox.
      https://sites.lsa.umich.edu/ocbaxtersagart/

  UW MA thesis, Ming-dynasty Uyghur transcriptions — 1,040 Turkic terms in the appendix.
      https://digital.lib.washington.edu/researchworks/items/e5c21e6f-7df6-4e19-ae9a-16231ec135c2
      The only collated Turkic-Chinese resource that exists. Extract the tables.

  Sogdian control set — hand-extract ~35 pairs from Yoshida's Iranica article (~1 hour).
      https://www.iranicaonline.org/articles/personal-names-sogdian-1-in-chinese-sources/

  Secret History of the Mongols — use the ja.wikisource XML dump, not per-page fetches.
      https://ja.wikisource.org/wiki/音訳蒙文元朝秘史

  ASJP v19 CLDF (CC BY 4.0) — Yeniseian phonotactic prior.
      https://zenodo.org/records/3843469
NOTE

echo
echo "Files now in $DEST:"
ls -la "$DEST" 2>/dev/null | tail -n +2
