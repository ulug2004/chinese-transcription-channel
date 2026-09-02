# chinese-transcription-channel

Corpora, channel models and evaluation code for **Chinese transcriptions of steppe names** —
Mongolian, Turkic and Sanskrit words written in Chinese characters, and what can (and cannot)
be recovered about how they sounded.

Author: Aziz M. Uluğ, PhD · Cortechs.ai
Companion write-up: `docs/paper_plain_language.html`

---

## What this is

Chinese scribes wrote foreign names by choosing characters that sounded close. That process is
a **noisy channel**: source sound in, Chinese spelling out. This repository learns that channel
from aligned examples, measures how far it can be inverted, and states plainly where it fails.

The headline result is negative and deliberate: at the data density available for Xiongnu names
(~1.4 observations per character), **whole-form reconstruction and language attribution are not
supportable**. What *is* supportable is a bounded set of claims about initial consonants and
nasal endings. The corpora, not the reconstructions, are the durable output.

## Outputs

### Corpora (`data/derived/`) — the primary contribution

| File | Size | What it is |
|---|---|---|
| `shm_transcription_pairs.csv` | 9,329 | Mongolian–Chinese pairs from the *Secret History of the Mongols* |
| `ligeti_turkic_chinese_pairs.csv` | 594 | Turkic–Chinese pairs from Ligeti's Sino-Uyghur glossaries (see licensing) |
| `nti_transcription_pairs.csv` | 1,017 | Sanskrit–Chinese pairs, phonetically verified (音譯 separated from 意譯) |
| `nti_rejected.csv` | 7,480 | Entries rejected by that filter, retained so the decision is auditable |
| `aksara_table.csv` | 845 | Induced akṣara → character mappings (matches the standard inventory) |
| `xiongnu_rulers_reconstructed.csv` | 23 | Rulers and clan names with Later Han readings |
| `xiongnu_titles_lexicon_reconstructed.csv` | 16 | Titles and lexical items with Later Han readings |
| `uyghur_coda_characters.csv` | 173 | Coda-table characters with Pulleyblank EMC readings |

Two of these — the *Secret History* and Ligeti sets — were extracted from sources that had
never been available in machine-readable form.

### Models and measurements

| File | What it is |
|---|---|
| `channel_emissions_*.csv` | Trained emission tables (reading-anchored, with backoff) |
| `learning_curve.csv` | Accuracy vs. number of training pairs |
| `period_gap.csv` | Ming → Later Han survival, split by phonological component |
| `initial_correspondence.csv` | Source onset × Chinese initial, all three corpora |
| `modern_echo_candidates.csv` | Modern Turkish/Kazakh dictionary matches, each with a p against the null |
| `lexicon_variants.csv` | Six lexicons (raw, loan-filtered, union, intersection), each with its own null |
| `dlt_lexicon.csv` | 6,880 headwords with Turkish glosses, extracted from the TDK index of Divanu Lugati't-Turk |
| `old_turkic_echo.csv` | The dictionary search run against that 11th-century lexicon |
| `cuman_lexicon.csv` | 2,110 Cuman headwords with Latin glosses, from Kuun's 1880 Codex Cumanicus. **Public domain source — this one is releasable** |
| `cuman_echo.csv` | The search run against the Cuman lexicon |

## Method, in one paragraph

Characters are aligned to phoneme chunks by **EM**, producing P(character | sound). Emission
tables are **reading-anchored** with backoff (full reading → onset+rime → onset → global), so a
character never seen in training still receives a distribution. Evaluation is always on held-out
data, with **document-level holdout** for the Mongolian corpus (unseen chapters, not a random
split) and permutation / random-repairing **null models** for every comparison. Negative controls
are run on cases whose answer is already known — they are what exposed the failures.

## Reproducing

Scripts in `src/` are numbered and run in order; each is rerunnable on its own.

```
src/step1_parse_nti.py            音譯 / 意譯 separation by phonetic verification
src/step3_fill_reconstructions.py join names to Later Han readings (Unihan variant resolution)
src/step4_channel_model.py        EM channel training
src/step5_language_comparison.py  Bayes-factor language comparison + prior-ceiling diagnostic
src/step6_prior_adequacy.py       24-cell prior-adequacy experiment
src/step7_reconstruct.py          decoding with a language-neutral prior; reachability ceiling
src/step8_extract_shm.py          Secret History extraction
src/step9_segmental_channel.py    segmental channel
src/step10_learning_curve.py      data-vs-architecture ablation
src/step11_reading_anchored.py    reading-anchored emissions (gated on out-of-domain accuracy)
src/step12_extract_ligeti.py      Ligeti glossary extraction
src/step13_turkic_channel.py      Turkic channel
src/step14_period_gap.py          Ming → Later Han component survival
```

Windows users: matching `RUN-*.bat` launchers are provided.

`data/external/` holds third-party inputs and is **not** redistributed; fetch scripts and
checksums are provided instead.

## Licensing

- Code: MIT.
- `my_resources/` is **not** part of the repository. It holds third-party source texts
  (dictionaries, editions, scanned volumes) that the extraction scripts read locally. Some are
  public domain — the Kuun 1880 *Codex Cumanicus*, Abu Hayyan's *Kitab al-Idrak* — and some are
  in copyright. None are redistributed here. `.gitignore` it.
- Derived corpora: CC-BY-4.0, **except** `ligeti_turkic_chinese_pairs.csv`. The Ligeti glossaries
  are under copyright to Akadémiai Kiadó and redistribution permission is unresolved. The
  extraction script is released; the pair file is withheld pending clearance. Anyone with
  legitimate access to *Acta Orientalia ASH* 19 (1966) and 22 (1969) can regenerate it.

## Known traps (documented in `docs/design_notes.md`)

These cost real time and are worth reading before extending the work:

1. Corpora of unequal size make thinner models win by being vague — equalise before comparing.
2. Emission tables must cover every character the decoder can back off to, not just seen ones.
3. Gate reconstruction quality on **out-of-domain** accuracy; in-domain accuracy will lie to you.
4. Never report an aggregate coda figure — split nasal from stop; the sample is not balanced.
5. Schuessler prints 虚 撐 户 脱 禄 where the histories print 虛 撑 戶 脫 祿. Resolve via Unihan.
6. In the *Secret History* text, character + U+180B is an annotation and must be dropped.
7. Journal running heads carry the author name on verso pages — filter both, or lose half the text.

## A result worth knowing about

`step15_initial_probe.py` counts how often a source word beginning in `b-` was written with a
Chinese `m-` character: **3 times in 838 opportunities**, all three in the Sanskrit set. The
standard reading of the Xiongnu founder 冒頓 (*mək-tuən) as *baγatur requires exactly that
substitution, since Proto-Turkic has no initial *m-. Scribes had a voiced `b-` series and used
it. Together with the absent `-r`, this is a second independent line against that etymology.

## Do not skip the null model

`step16_modern_echo.py` looks the readings up in modern Turkish and Kazakh dictionaries. It
finds matches for almost everything — and so does a meaningless string: **278 of 300
pseudo-names** built by shuffling Later Han syllables also find a Turkish dictionary word at
the same threshold. Both cases where the answer is independently known (撑犁 = *tengri*,
頭曼 = *tümen*) are lost to an unrelated modern word. Treat the candidate column as the noise
floor, not as etymology.

`step17_lexicon_variants.py` tests the two obvious fixes. Filtering loan-shaped words out of
Turkish raises the noise floor from 0.156 to 0.200 — real, but not enough. **Pooling Turkish
and Kazakh makes it worse** (0.156 → 0.117): a bigger word list finds more matches for the
real names *and* for the meaningless ones. Intersecting the two lexicons is the operation that
helps (→ 0.372), but it deletes the cognates it was meant to isolate — Turkish `tanrı` and
Kazakh `täñir` are the same word and do not match as strings, so both drop out, while
`domino` and `kauçuk`, borrowed into both recently, survive.

`step18_old_turkic.py` does the search that should have been done first: against Kaşgarli
Mahmud's *Divanu Lugati't-Turk* (1072-77), the earliest Turkic dictionary, extracted from the
TDK index volume. Noise floor 0.200, and **both known answers return** — `tengri` 4th for
撑犁 (Kaşgarli's own gloss: *gok, sema*, "sky, heaven", independently matching the Hanshu's
天) and `tumen` 3rd for 頭曼. Neither ranks first, and 3 of 36 names clearing p<=0.05 is still
chance. But against a modern lexicon both were invisible, so part of the earlier failure was
the lexicon, not the method.

`step19_codex_cumanicus.py` adds a third lexicon: the Kipchak Turkic of the Codex Cumanicus
(c. 1300), from Kuun's public-domain 1880 edition. The noise floor rises again to **0.242**, the
highest of six lexicons, and `tengri` "deus" reaches **2nd** for 撑犁 — its best rank anywhere.

The other thing it turned up cuts against the accepted etymology of 頭曼. `tümen` "ten thousand"
is absent from the Cuman vocabulary entirely, and in every lexicon that has both, the search
prefers a different lexeme: Turkish `duman`, Kasgarli's `tuman` "duman, sis", Cuman `touman`
"nebula" — smoke/fog/mist, one word across three lexicons and a thousand years. The difference
is a vowel and step 14 puts vowel recovery at 50%, so it settles nothing; it is recorded because
the alternative is never raised in the literature.

Two bugs were found by asking why a known answer was missing, which is the only reliable way:
Chinese had no `r-` and writes it `l-` (12 of 14 attestations in `initial_correspondence.csv`),
so l/r must not be priced as a generic mismatch; and the segmenter was silently discarding a
bare `ŋ`, which removed `tengri` from the search entirely.

Note: the headword count varies by pypdf version (6,820 vs 6,880 across two machines), which
shifts the noise floor by ~0.008 and nothing else. Pin pypdf if you need byte-identical output.

Rebuild the null for every lexicon. Counting matches without recomputing it makes every
enlargement look like an improvement.

Requires `hunspell-tr` and `hunspell-kk` (`apt install hunspell-tr hunspell-kk`) and, for the
frequency filter, `pip install wordfreq`.

## Citation

> Uluğ, A. M. (2026). *chinese-transcription-channel*: corpora, channel models and evaluation
> code for Chinese transcriptions of steppe names [software and data].
> https://github.com/ulug2004/chinese-transcription-channel

Archived release to be deposited with Zenodo; DOI on first release.
