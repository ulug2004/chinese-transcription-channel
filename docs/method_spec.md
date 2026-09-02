# Method Specification

**Project:** Probabilistic reconstruction of steppe onomastics from Chinese transcriptional
evidence, with quantified support for competing ethnolinguistic hypotheses.

Draft v0.1 — 2026-08-26

---

## 1. What this is and is not

**Not:** a Chinese→Turkic translation model.
**Is:** a model-comparison framework that scores how well each candidate language explains
an attested Chinese transcription.

The distinction is the whole design. A seq2seq model trained Chinese→Turkic will emit a
plausible Turkic form for *any* input — Sogdian, Yeniseian, Tocharian, or noise. It has no
capacity to decline. Fluency would be mistaken for evidence, and every conclusion would be
unfalsifiable.

---

## 2. Task formulation

Let `c` be an attested Chinese transcription (a character sequence), and let
`L ∈ {Old Turkic, Yeniseian, Mongolic, Middle Iranian, Tocharian, ...}` be candidate
source languages.

Compute, for each `L`:

```
P(c | L) = Σ_n  P(c | n) · P(n | L)
```

where `n` ranges over possible source-language forms.

- **`P(c | n)`** — the *transcription channel*: how a scribe of period T would render the
  foreign phonological string `n` in Chinese characters.
- **`P(n | L)`** — the *source prior*: how likely `n` is as a word/name in language `L`,
  from that language's phonotactics and lexicon.

Report **Bayes factors** `P(c | L1) / P(c | L2)` between hypotheses, with uncertainty.

The framework can and must be able to return "inconclusive."

---

## 3. Pipeline

```
Chinese characters
      ↓  [period-appropriate reconstruction table]
Reconstructed Chinese phonological string   (Later Han | EMC | LMC | Old Mandarin)
      ↓  [transcription channel, inverted]
Distribution over source-language phoneme strings
      ↓  [phonotactic + lexical prior per language L]
P(c | L) for each candidate L
      ↓
Bayes factors + calibrated uncertainty
```

**Step 1 is non-negotiable and is where naive approaches fail.** Modern Mandarin has lost
the final stops (-p/-t/-k), the voiced initials, and final -m that carry nearly all the
signal. 突厥 is *Türk* in Early Middle Chinese and *Tūjué* in Mandarin; the /t/ and /k/
codas that identify the word were deleted a thousand years ago.

**Date-stratify the reconstruction table:**

| Material | Period | Layer | Dataset |
|---|---|---|---|
| Xiongnu | c. 200 BCE – 200 CE | **Later Han Chinese** | Schuessler `LHantab.tsv` (CC0) |
| Göktürk / Tang | c. 550 – 900 CE | Early Middle Chinese | nk2028 → Baxter MC |
| Yuan / Mongol | c. 1200 – 1400 CE | Old Mandarin | 中原音韻, 蒙古字韻 |
| Ming glossaries | c. 1400 – 1600 CE | Early Mandarin | 洪武正韻 |

---

## 4. The transcription channel

### 4.1 Training data

No Turkic-Chinese training set exists (see `references/corpus_audit.md`, §C). The channel
is therefore learned by **cross-lingual transfer** from languages that *do* have aligned
data:

| Source | Pairs | Role |
|---|---|---|
| NTI / Fo Guang Shan Sanskrit-Chinese | ~9,688 raw → ~3,000-5,000 after filtering | primary training |
| NTI `phonetic`-tagged characters | 191 chars → 88 Sanskrit aksaras | **prior initialization** |
| DILA authority DBs | 1,071 name pairs | training |
| Secret History of the Mongols | 12 juan aligned | training (Yuan layer) |
| Baley Late Han v7 | 401 | **held-out gold eval** |
| UW thesis 高昌館雜字 appendix | 1,040 Uyghur terms | **Turkic-specific fine-tune** (requires PDF extraction) |

**Critical preprocessing:** the Sanskrit-Chinese pairs mix 音譯 (phonetic transcription)
with 意譯 (semantic calque). 釋迦牟尼 = *śākyamuni* is transcription; 大乘 = *mahāyāna* is
calque. Training on calques would teach the channel nonsense. Filter with a syllable-count
vs character-count heuristic, seeded and validated against the 191 `phonetic`-tagged
characters.

### 4.2 Model

Start with a **weighted finite-state transducer** or noisy-channel model over phonemes,
not a neural seq2seq. Reasons:

1. Data is small (thousands, not millions of pairs).
2. Historical linguists need to see *why* a reconstruction was proposed. An FST composition
   is inspectable; a transformer's attention is not an argument.
3. The 191-character aksara table gives a hand-built emission prior that drops directly
   into a WFST but is awkward to inject into a neural model.

Escalate to a neural scorer only if the WFST underperforms on the Baley gold set, and keep
phonotactic constraint decoding either way. A hybrid — neural scoring, FST constraints — is
the likely sweet spot.

### 4.3 Channel features to model explicitly

- Coda deletion/preservation (the Ming Uyghur thesis is specifically about this)
- Cluster simplification (foreign CC → Chinese CV.CV)
- Vowel epenthesis
- Scribe/period identity as a conditioning variable (An Shigao vs Lokakṣema differ)
- Character-choice conventions: semantic bias, pejorative character selection for
  ethnonyms (匈奴 is a live risk — see `data/xiongnu_titles_lexicon.csv` T15)

---

## 5. Source priors P(n | L)

| Language | Source | Status |
|---|---|---|
| Old Turkic | Clauson EDPT | **print only — manual keying required** |
| Yeniseian | ASJP v19 CLDF, StarLing | available |
| Mongolic | SHM romanization, Middle Mongol lexica | available |
| Middle Iranian | Lurje (print), Iranica article | partial |
| Tocharian | CEToM | check availability |

Where a lexicon is unavailable, fall back to an **n-gram phonotactic model** over whatever
attested corpus exists. Document this asymmetry — unequal prior quality across languages is
a confound that must be reported, not hidden. Consider a calibration step that normalizes
for prior strength.

---

## 6. Evaluation

### 6.1 Reconstruction accuracy
Held-out Baley Late Han items (401, with Later Han + MC + OC + Gāndhārī on both sides).
Metrics: phoneme error rate, top-k accuracy, calibration (are stated 80% intervals right
80% of the time?).

### 6.2 Negative controls — **the credibility experiment**

Run the classifier on items whose language is not in dispute:

| Control set | Expected verdict |
|---|---|
| Sogdian names in Chinese sources | Iranian |
| Buddhist Sanskrit terms | Indic |
| Tocharian, Tibetan, Baekje names | respective families |
| Secret History Mongolian | Mongolic |

**If the method assigns Sogdian names to Turkic, the method is broken** — and you learn
that cheaply, before publication. If it clears the controls and *then* says something about
the Xiongnu, the result is worth reading. This validation costs a week and is worth more
than any architecture decision.

### 6.3 Comparison to manual scholarship
Existing reconstructions (Pulleyblank, Vovin, Bailey, Clauson) are the baseline and the
gold standard. The contribution is not beating them — it is systematizing and quantifying.

---

## 7. Known limitations — state these before a reviewer does

1. **Names are weak evidence for ethnicity.** Names cross linguistic boundaries constantly:
   Turkic tribes bore Iranian names, Mongol rulers used Turkic titles, dynasties adopted
   the onomastics of prestige neighbours. A Turkic-sounding royal name is compatible with a
   non-Turkic-speaking population. This is the leading critique and it is fair.

2. **Titles are better evidence than personal names.** Institutional vocabulary (單于,
   撑犁, 屠耆, 谷蠡) is somewhat less mobile. Weight the corpus accordingly.

3. **Glossed items are the best evidence of all.** Where a Chinese source *translates* the
   foreign word — 撑犁 = 天, 孤塗 = 子, 屠耆 = 賢, the Jie couplet — meaning and form are
   both constrained. These few items carry more weight than dozens of unglossed names.

4. **n is small.** ~30-60 Chanyu names, ~15 titles. With borrowing noise, the evidence may
   simply not separate the hypotheses. A calibrated "inconclusive" is a legitimate and
   publishable finding in a debate this contested.

5. **Prior quality is unequal across languages** (§5). This biases toward whichever language
   has the best lexicon. Must be measured and reported.

6. **Reconstruction uncertainty compounds.** Later Han and Old Chinese reconstructions are
   themselves contested. Propagate that uncertainty rather than treating a single
   reconstruction as fact — run the pipeline under Schuessler, Baxter-Sagart, and Zhengzhang
   and report the spread.

---

## 8. Preregistration and bias control

This question is politically loaded. Turkic origin of the Xiongnu is entangled with Turkish
national historiography, as competing claims are with Mongolian and Chinese ones. A reader
will assess motive before method.

The defense is not avoidance. It is a design that could have returned a different answer,
and evidence that it does:

- **Preregister** the evaluation protocol, control sets, and decision rule before running
  on Xiongnu material.
- **Report all hypotheses' likelihoods** with equal prominence — Yeniseian and Iranian
  numbers in the same table and the same font as Turkic.
- **Publish the negative-control results** whether or not they flatter the method.
- **Report per-item results, not an aggregate verdict.** If different names pattern to
  different languages, that is a quantitative demonstration of the multiethnic-confederation
  hypothesis the 2023 aDNA work supports — a more interesting and more defensible result
  than a monolithic answer.

---

## 9. Positioning

**The contribution is the method, not the reconstructions.** Many of these names have been
reconstructed by hand (Pulleyblank, Vovin, Golden, Clauson). Claiming discovery invites a
reviewer who knows that literature to reject the paper. Claim instead:

> a reproducible probabilistic framework for evaluating competing language hypotheses from
> transcriptional evidence, with calibrated uncertainty, validated on known-language
> control corpora — applied to a long-contested case.

Secondary contribution: the **cross-lingual transfer** setup. Because no Turkic-Chinese
training data exists, the channel must be learned from Sanskrit and Mongolian and
transferred. That is a harder and more interesting problem than supervised mapping, and it
generalizes to any under-documented language attested only through a foreign script.

**Venues:** SIGTYP (ACL workshop; has run cognate-reflex-prediction shared tasks — closest
existing task formulation), LChange, SIGMORPHON. For the linguistics-side framing:
Journal of Historical Linguistics, Diachronica, Central Asiatic Journal.

---

## 10. Immediate next steps

1. Acquire Schuessler `LHantab.tsv` + `OCMtab.tsv` (CC0) — mirror.
2. Acquire NTI dictionary; extract the 9,688 pairs and the 191-character aksara table.
3. Build the 音譯/意譯 filter; validate against the 191 tagged characters.
4. Acquire Baley v7 as gold eval; hold out entirely.
5. Fill the `PENDING` reconstruction columns in `data/*.csv` from Schuessler.
6. Extract the 1,040-term appendix from the UW Gaochang thesis PDF.
7. Hand-extract Sogdian control pairs from the Iranica article (~1 hour).
8. Baseline WFST channel; evaluate on Baley; then controls.
