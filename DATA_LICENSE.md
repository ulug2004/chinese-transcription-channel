# Licensing of the data

The **code** in `src/` is MIT — see `LICENSE`.

The **data** is not uniform, because the sources are not uniform. Three cases:

## 1. Released here, CC BY 4.0

New alignments and extractions produced by this work, from sources that are
public domain or openly licensed:

| File | Source it derives from |
|---|---|
| `data/derived/shm_transcription_pairs.csv` | *Secret History of the Mongols*, 13th c. |
| `data/derived/nti_transcription_pairs.csv` | Buddhist terminology, open data release |
| `data/derived/nti_rejected.csv`, `nti_ambiguous.csv`, `nti_calques_excluded.csv` | as above |
| `data/derived/aksara_table.csv` | induced from the above |
| `data/derived/cuman_lexicon.csv` | Kuun (1880), **public domain** |
| `data/derived/cuman_echo.csv`, `old_turkic_echo.csv`, `modern_echo_candidates.csv` | search results |
| `data/derived/coda_spelling.csv`, `initial_correspondence.csv`, `period_gap.csv`, `learning_curve.csv`, `lexicon_variants.csv` | measurements |
| `data/derived/xiongnu_*.csv` | Chinese histories + Schuessler's published readings |
| `reports/*.txt` | run logs |

Attribution: Uluğ, A. M. (2026), *chinese-transcription-channel*.

## 2. Withheld — the extraction script is released instead

These are reproducible by anyone holding the source. The script is in `src/`;
run it against your own copy and you will get the same file.

| Withheld file | Source | Script |
|---|---|---|
| `data/derived/ligeti_turkic_chinese_pairs.csv` | Ligeti (1966, 1969), *Acta Orientalia ASH* — © Akadémiai Kiadó | `src/step12_extract_ligeti.py` |
| `data/derived/dlt_lexicon.csv` | Türk Dil Kurumu index to the *Dīwān Lughāt al-Turk* | `src/step18_old_turkic.py` |

No permission has been sought for redistribution of either, and none is needed
for this arrangement: the paper's numbers are checkable by re-running the
extraction, which is the point.

## 3. Not in this repository at all

`my_resources/`, `Downloads/` and `data/external/` hold third-party source
texts and datasets — dictionaries, scanned volumes, Unihan, the DILA authority
files. They are inputs, not outputs, and are excluded by `.gitignore`. Where a
script needs one, its docstring says which file and where to obtain it.
