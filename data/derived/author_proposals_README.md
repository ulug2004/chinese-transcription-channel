# `author_proposals.csv` — 34 candidate readings

**These are not results.** They are the author's own readings of the Later Han
forms as Turkic names, offered for a specialist to accept or dismiss.

## Why they are here rather than in the paper

Section 5 of the paper measures exactly this operation — looking a reconstructed
reading up in a Turkic dictionary — against a null model built by resampling
Later Han syllables. Across six lexicons, from modern Turkish to the *Codex
Cumanicus*, between one and three names in thirty-six clear p ≤ 0.05, which is
what thirty-six coin flips give. Doing the matching by hand does not improve on
the algorithm; it makes it worse, because a person cannot help preferring the
reading that means something, and that preference is the selection effect the
null exists to measure.

Publishing 34 such readings inside a paper that demonstrates their unreliability
would be incoherent. Withholding them entirely would be worse: readers will run
this search in their heads regardless, and it is better that the results are
written down, dated, and labelled.

## The one exception, which is in the paper

The recurring title element 若鞮 (*ńɑk te*) is argued in the paper itself, because
it is supported differently:

- the *Hou Hanshu* glosses it 孝 "filial" — the meaning is recorded, not inferred;
- *inak* is attested as *fidelis* "faithful" in the *Codex Cumanicus* (Kuun 1880,
  p. 182), so the sense is documented in a medieval source;
- the morphology is licensed: *-t* is an Old Turkic plural used with titles
  (*tegin* → *tegit*), and the alternative *-tI* is ruled out by counting — of 31
  Cuman headwords in *-tI*, almost all are past-tense verbs;
- the spelling objection was measured and dismissed: 30% of stop-final source
  syllables were written with an open Chinese character.

That is the standard a proposal has to meet. None of the 34 below meets it.

## Columns

| Column | Meaning |
|---|---|
| `chinese` | as written in the histories |
| `pinyin` | modern Mandarin, for reference only |
| `later_han` | Schuessler's published reconstruction — **not** model output |
| `turkish_render` | the same reading in Turkish orthography |
| `proposed_name` | the author's reading |
| `proposed_sense` | the sense proposed for it |
| `note` | historical or comparative remark, where offered |
| `status` | normally constant — these carry no support from any measurement in the paper. One row, 且渠, is marked differently: see below. |

## How to disagree

`src/lookup_lexicons.py` searches all four lexicons at once and folds the
Turcological and Turkish spelling variants (q≡k, ñ≡ng, ş≡s, ı≡i). Type a
proposed form and see what the medieval sources actually have. That is how the
*Codex* attestation for *inak* was found, and how the *-tI* count was made.

## The two rows most likely to be queried

`且渠` is read **Çaka** "the striker", from the verb *çak-*. The spelling is permitted by the
step-15 initial-correspondence counts, but no *çaka* headword exists in Kāşgarî, the *Codex
Cumanicus* or Clauson — only *çak-* and its derivatives — and the Chinese sources do not record what
the office did, so no sense can be tested.

`稽粥` is read **Kiçük** "the younger". The sense is attested three times over — Kāşgarî *kiçik /
kiçük* "small", *Kutadgu Bilig* 1823, and the *Codex Cumanicus* *Kečak* *paucus* — in a native word,
and 粥 *tśuk* actually writes the final -k. 稽粥 is the personal name of Laoshang chanyu, Modu's son
and successor, so "the younger" fits the recorded succession. What is missing is a Chinese gloss to
test the sense against, and the vowel is unrecoverable.

Supplement §S1.5 explains why no reading in this file is supported by quoting the decoder's own
ranked output.
