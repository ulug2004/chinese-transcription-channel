# Design Notes and Decision Log

A record of what was considered and why it was rejected. Kept because the discarded
options matter as much as the chosen one — and because a reviewer will ask.

Sessions: 2026-08-26

---

## 0. The idea as originally stated

> Chinese writes with characters and lacks many foreign sounds, so scribes chose the
> closest available characters. Old Chinese records name many Turkic kings and tribes.
> Use modern Turkish names and their Chinese-character spellings as a training set, learn
> the mapping, then invert it on the old records to recover how those names really sounded.

Sound instinct, fatal implementation. What follows is why.

---

## 1. REJECTED: training on modern Turkish → modern Mandarin pairs

**The flaw.** Modern Mandarin is not the language the records were written in. Between the
Han/Tang periods and today Chinese lost:

- final stop consonants (-p, -t, -k)
- voiced initials
- final -m
- and underwent extensive palatalization

The transcriptions were accurate — to a phonology that no longer exists.

| | |
|---|---|
| Written | 突厥 |
| Modern Mandarin | Tujue |
| Early Middle Chinese | *dwət-kuat |
| Actual name | **Türk** |

The /t/ and /k/ codas that carry the entire identification were deleted a thousand years
ago. A model trained on modern readings cannot recover them, because they are not in its
input.

**It is a triple domain shift, all three in the wrong direction:**

1. **Target side** — Modern Mandarin ≠ Later Han / Middle Chinese.
2. **Source side** — Modern Turkish ≠ Old Turkic. Worse, modern Turkish given names are
   overwhelmingly Arabic and Persian (Mehmet, Mustafa, Ayşe); Old Turkic onomastics look
   nothing like them (Tonyukuk, Kül Tigin, Qapağan, Ishbara, Bilge).
3. **Convention** — modern Chinese transcribes foreign names through a fixed standardized
   table (Xinhua 世界人名翻译大辞典). Tang scribes had no table and improvised phonetically.
   Training on the modern table teaches a bureaucratic lookup, then applies it to ad-hoc
   phonetic writing.

**Decision:** work in reconstructed phonemes, not characters. Map each character to its
period-appropriate reconstruction first (Later Han for Xiongnu, EMC for Göktürk), then the
task becomes a phoneme-to-phoneme transduction. See `method_spec.md` §3.

---

## 2. REJECTED: any Chinese → Turkic seq2seq model

**The flaw.** A seq2seq model always outputs something. Trained Chinese→Turkic, it will
produce a plausible Turkic name for 冒頓 — and equally for a Sogdian name, a Yeniseian
name, a Tocharian name, or noise. It has no capacity to decline, because it was never given
the option.

This matters more than it sounds. The project's actual goal is **ethnolinguistic
attribution** — determining whether a dynasty was Turkic. A model that returns Turkic
readings for everything cannot answer that question, and every conclusion drawn from it is
unfalsifiable. Fluency would be mistaken for evidence.

**Decision:** reformulate as model comparison. Build P(transcription | language L) for
several candidate languages, compare via Bayes factors, and allow "inconclusive" as an
outcome. See `method_spec.md` §2.

---

## 3. REJECTED: neural transformer as the first model

Not wrong in principle, wrong as a starting point:

1. The data is small — thousands of pairs, not millions.
2. Historical linguists need to see *why* a reconstruction was proposed. An FST composition
   is inspectable; attention weights are not an argument.
3. The 191-character akṣara table (from the NTI dictionary) is a hand-built emission prior
   that drops straight into a WFST and is awkward to inject into a neural model.

**Decision:** start with a weighted finite-state transducer / noisy-channel model. Escalate
to neural scoring only if the WFST underperforms on the Baley gold set, and keep
phonotactic constraint decoding either way.

---

## 4. CORRECTED: the Orkhon inscriptions are not a parallel corpus

I initially described the Kül Tigin and Bilge Kagan stelae as bilingual ground truth. That
was **wrong**. The monuments do carry a Chinese face, but it is an **independent Chinese
composition, not a transcription of the Turkic text**. It provides zero phoneme-mapping
signal.

Consequence: there is no ready-made Turkic-Chinese parallel corpus anywhere. Tang-era
Chinese transcription of Turkic survives only as scattered, uncollated names in the
dynastic histories.

---

## 5. The data verdict (see `references/corpus_audit.md` for detail)

**GO, on a different base than assumed.**

Available:
- Schuessler's Later Han + Minimal Old Chinese reconstructions, **CC0**, deposited by the
  author Dec 2024. Exactly the Xiongnu-period layer. Did not exist as data 18 months ago.
- ~9,688 Sanskrit-Chinese pairs (NTI / Fo Guang Shan), including **191 characters tagged
  `phonetic`** mapping single characters to 88 Sanskrit akṣaras — a hand-built per-phoneme
  confusion prior.
- 401-item Baley Late Han gold set with reconstructions on both sides.
- Secret History of the Mongols, 12 juan, Chinese characters aligned with romanized Mongolian.

Not available:
- **高昌館譯語**: no dataset exists. One PDF thesis appendix with 1,040 Uyghur terms is the
  only collated Turkic-Chinese resource in the world.
- **Pulleyblank's Lexicon**: print only, no digitization anywhere.
- **Clauson's EDPT**: page scans only.
- **Sogdian onomasticon (Lurje)**: print only.
- **DDB bulk**: contractually and technically blocked; the public extract has no Sanskrit field.

**Consequence for the framing:** because there is no Turkic training data, the channel model
must be learned from Sanskrit and Mongolian and **transferred**. This is a harder problem
than supervised mapping — and a better paper. It generalizes to any under-documented
language attested only through a foreign script.

---

## 6. Framing decisions

### The contribution is the method, not the reconstructions
Many of these names have been reconstructed by hand — Pulleyblank, Vovin, Golden, Clauson,
Bailey. Claiming discovery invites rejection from any reviewer who knows that literature.
The claim is a reproducible probabilistic framework with calibrated uncertainty, validated
on known-language controls, applied to a contested case. Existing manual reconstructions are
the baseline and the gold standard, not the competition.

### Negative controls are the credibility experiment
Run the classifier on items whose language is not in dispute — Sogdian, Sanskrit, Tocharian,
Tibetan, Mongolian. If it calls the Sogdian names Turkic, the method is broken, and that is
learned cheaply and before publication. If it clears the controls and *then* says something
about the Xiongnu, the result is worth reading. One week of work, worth more than any
architecture decision.

### Titles and glossed items over personal names
Names cross linguistic boundaries constantly. Institutional vocabulary is somewhat less
mobile. **Glossed items are best of all** — where a Chinese source translates the foreign
word (撑犁 = 天, 孤塗 = 子, 屠耆 = 賢, the Jie couplet), both form and meaning are
constrained. A handful of these outweigh dozens of unglossed names.

### Political exposure is a design problem, not a topic to avoid
The Turkic-Xiongnu question is entangled with Turkish national historiography, as competing
claims are with Mongolian and Chinese ones. A reader will assess motive before method.

The defense is a design that could have returned a different answer, plus evidence that it
does: preregister the protocol, report all hypotheses' likelihoods with equal prominence,
publish control results whether or not they flatter the method, and report per-item rather
than aggregate results.

If different names pattern to different languages, that is a quantitative demonstration of
the multiethnic-confederation hypothesis the 2023 aDNA work supports — a more interesting
and more defensible finding than a monolithic verdict.

---

## 7. Open questions

- Does the Sanskrit-trained channel actually transfer to Turkic? This is the project's
  central empirical risk and should be tested early, on the 1,040-term Uyghur set, before
  building anything else.
- How much does prior quality asymmetry across languages bias the comparison? Old Turkic has
  Clauson (print); Yeniseian has ASJP wordlists. Unequal, and it must be measured.
- Can reconstruction uncertainty be propagated cleanly? Running the pipeline under
  Schuessler, Baxter-Sagart and Zhengzhang and reporting the spread is the honest approach,
  but it may widen intervals past usefulness.
- Is n simply too small? ~30-60 Chanyu names, ~15 titles, with heavy borrowing noise. A
  calibrated "inconclusive" must be an acceptable outcome, or the project is not honest.

---

## 8. Two negative results (2026-08-26)

The pipeline was built through to inference. Two components do not work, both for
measurable reasons. Recording them here because they are the substantive findings,
and because someone will otherwise try the same thing again.

### 8.1 REJECTED: language attribution from phonotactic priors

**Step 5** built the Bayes-factor comparison the method spec called for, and it
failed its own controls: Ming Uyghur transcriptions came out Turkic 8.6% of the
time against a 16.7% chance floor.

**Step 6** established that the bottleneck is the prior, not the channel, by
handing the priors the TRUE source word - no Chinese, no channel:

| prior | corpus | hypothesis set | accuracy | chance |
|---|---|---|---|---|
| n-gram | true Uyghur | Turkic vs Yeniseian | 60.4% | 50% |
| features | true Uyghur | Turkic vs Yeniseian | 57.7% | 50% |
| features | true Uyghur | Turkic vs Yeniseian (>=4 vowels) | 69.0% | 50% |
| features | true Sanskrit | all 5 families | **13.9%** | 20% |

That last row is the damning one: a prior that systematically prefers the WRONG
family is biased, not merely weak.

Both a generic character n-gram and a targeted linguistic feature model (backness
harmony, the Old Turkic ban on initial l-/r-/n-, initial clusters, maximum
consonant run) were tried, across four length strata and two hypothesis sets.
Nothing reached a usable margin.

**Causes, in order of severity:**
1. Turkic, Mongolic and Tungusic are genuinely near-identical phonotactically.
   This is a fact about the languages, not a modelling gap.
2. ~half of ASJP Swadesh entries are monosyllables, where vowel harmony - the
   single best Turkic/Yeniseian discriminator - is undefined.
3. Equalising corpora to 469 forms is *necessary* (otherwise thin data wins by
   producing flatter models) but leaves too little to estimate anything sharp.
4. ASJP's 41-symbol alphabet discards the detail that separates neighbours.

**Blocked on:** manual lexicon keying - Clauson (print), a real Yeniseian lexicon,
Middle Mongol and Middle Iranian onomastica. Ideally ONOMASTIC data, since names
have their own phonotactics and names are what the question is about.

### 8.2 REJECTED: whole-form pronunciation reconstruction

The pivot - drop attribution, output ranked pronunciations, let readers judge
affiliation - is a better-posed project (it is evaluable; attribution is not).
**Step 7** built it with a language-neutral universal prior. It also does not
reach usable accuracy:

| gold set | reachable | exact | within 1 | within 2 | mean norm. edit dist |
|---|---|---|---|---|---|
| Baley Late Han Sanskrit | 100% | 8.2% | 17.4% | 32.8% | 0.410 |
| Ming Uyghur | 33% | 1.2% | 2.4% | 20.8% | 0.673 |

(best of 20 candidates)

**Why - and it is just arithmetic.** Step 4 measured per-position top-1 syllable
accuracy on Baley at 46.4%. Over a three-syllable name that compounds to
0.464^3 ~ 10%, and 8.2% is what we see. Nothing is broken; compounding kills
whole-form reconstruction.

**Second limit:** only 33% of Turkic gold forms are *reachable* at all, because
the channel's syllable inventory is Sanskrite-derived and cannot produce q or
front-rounded vowels.

### 8.3 What survives, and the one redesign that would matter

Surviving and validated:
- the 音譯/意譯 separation via phonetic verification (step 1)
- the channel model: 79.6% onset accuracy on an independent corpus (step 4)
- cross-lingual transfer to Turkic: +0.42 over a random-repairing null, p<0.005
  (steps 4 and the transfer test)

Both failures point at the same fix: **a segmental, reconstruction-anchored
channel.** Currently the channel is keyed on the CHARACTER, so every character is
its own parameter estimated from a handful of observations, and its output
vocabulary is whole Sanskrit syllables. Instead key it on the character's
RECONSTRUCTED READING (Later Han) mapped to individual SEGMENTS. That would:
  - share statistical strength across all characters with the same reading,
    which is where the data efficiency has to come from
  - remove the Sanskrit inventory ceiling, since any segment sequence becomes
    producible
  - raise per-position accuracy, which is the only thing that can lift whole-form
    accuracy out of the compounding trap

Until per-position accuracy is well above 46%, neither attribution nor whole-form
reconstruction is supportable, and saying so with measured ceilings is the
honest contribution.

---

## 9. The confound resolved: data was the binding constraint (2026-08-26)

Steps 5-7 failed, and the failures were consistent with two incompatible
explanations - the method is wrong, or 1,017 Sanskrit pairs is not enough. Those
were confounded, so neither could be acted on.

**Step 8** extracted the Secret History of the Mongols corpus from the aligned
epub: **29,306 triples -> 9,329 unique (Chinese transcription, romanised
Mongolian) pairs**, 37,250 character tokens over 535 characters (~70 observations
per character, against a handful before). 93.4% of pairs agree within +/-1
between character count and syllable count - the signature of a genuine
per-syllable transcription.

Format note worth keeping: in that edition a Chinese character followed by
MONGOLIAN FREE VARIATION SELECTOR ONE (U+180B) is a reading ANNOTATION on the
next character (舌 liquid/retroflex, 中 medial, 灰) and must be dropped, while a
character carrying U+180C or U+FE00 IS a transcription character and must be
kept. Reversing that rule silently produces a garbage corpus.

**Step 9** trained a segmental channel on it - characters mapping to 1-3
segments rather than whole Sanskrit syllables, which also removes the inventory
ceiling that made only 33% of Turkic gold forms reachable.

Evaluated by holding out whole DOCUMENTS (6 unseen chapters, 1,422 pairs), not a
random split, so there are no shared names or formulae between train and test:

| metric (best of top 20) | Sanskrit-trained, Baley | SHM segmental, unseen chapters |
|---|---|---|
| whole-form exact | 8.2% | **36.9%** |
| within 1 segment | 17.4% | **66.3%** |
| within 2 segments | 32.8% | **87.5%** |
| mean normalised edit distance | 0.410 | **0.150** |

Per-position: exact chunk top-1 52.8%, top-3 78.4%.

**Conclusion: the approach is sound. The earlier failures were about data volume,
not about the method.** Whole-form reconstruction moves from unusable to
genuinely useful once there are enough observations per character.

Caveat on one comparison: "first segment top-1" (65.8%) is NOT comparable to the
Sanskrit channel's "onset top-1" (79.6%) - the units differ, since a segment
chunk may begin with a vowel while a syllable onset is a consonant. Do not report
those two against each other.

Remaining error patterns, in order of frequency:
  1. vowel quality - u/ü and o/ö confusion, which Chinese transcription genuinely
     underdetermines; probably an irreducible floor rather than a modelling gap
  2. segment doubling (üCCidarmala for üCiDarmala) from adjacent chunks
     overlapping on a shared segment
  3. epenthetic vowels inserted where the chunk model prefers CV

### What this means for the Xiongnu question

The method works where data is adequate. The Xiongnu application is limited by
**Han-era data volume**, not by the approach. That makes the honest package:
  - the method, demonstrated and evaluated on Mongolian at document-level holdout
  - the Xiongnu case as a data-limited application with a measured bound
  - the two negative results of section 8 as quantified limits, not failures

---

## 10. The learning curve, and a correction to section 9 (2026-08-26)

Section 9 attributed the step-9 gain to "9x data + segmental units" without
separating the two. **Step 10 separates them, and the architecture contributes
essentially nothing.**

### Same architecture, Han-era data volume

Segmental channel on the 858 training Sanskrit pairs:

| | exact | within1 | within2 | mean ned |
|---|---|---|---|---|
| syllable architecture (steps 4/7) | 8.2% | 17.4% | 32.8% | 0.410 |
| **segmental architecture, same data** | **8.8%** | 22.5% | 39.2% | 0.437 |

**+0.6 points on exact match.** Segmental units remove the inventory ceiling
(only 33% of Turkic gold forms were reachable before), which matters for what the
model *can* produce - but they buy no accuracy when the data is thin. The entire
step-9 improvement was data volume.

### The curve (Mongolian, evaluation set held fixed on unseen chapters)

| train pairs | obs/char | pos top-1 | exact | within1 | within2 | mean ned |
|---|---|---|---|---|---|---|
| 500 | 9.5 | 33.9% | 7.3% | 26.9% | 53.5% | 0.341 |
| 1,000 | 15.4 | 31.7% | 6.4% | 28.7% | 58.5% | 0.329 |
| 2,000 | 23.8 | 39.7% | 13.5% | 45.7% | 70.6% | 0.252 |
| 4,000 | 39.8 | 43.1% | 19.3% | 54.0% | 78.6% | 0.209 |
| 7,530 | 60.8 | 53.5% | 36.4% | 69.8% | 89.3% | 0.142 |

Still climbing steeply at the top end - no plateau reached.

### The real finding: obs/char is the binding variable, not pair count

| corpus | observations per character |
|---|---|
| Mongolian, full | 60.8 |
| Mongolian, 500 pairs | 9.5 |
| Sanskrit, 858 pairs | 5.0 |
| **Xiongnu names + titles** | **1.4** (112 tokens / 81 distinct) |

The Sanskrit corpus is sparser per character than the *smallest* Mongolian
sample, because Buddhist transcription uses a sprawling character inventory while
the Secret History uses a tight conventionalised one. And the Xiongnu material
sits at ~1.4 observations per character.

**At 1.4 observations per character a character-keyed channel cannot be estimated
at all.** No search improvement, prior, or architecture recovers from that.

### The consequence - now empirically motivated, not a guess

For Han-era material the channel must key on the character's **reconstructed
reading** (Schuessler Later Han), not on the character. Characters sharing a
reading pool their evidence, the ~81 distinct Xiongnu characters collapse onto a
much smaller set of reading types, and each type draws observations from the whole
Buddhist corpus. That is the only route that changes the arithmetic, and it is
the next thing to build.

Bound to respect meanwhile: at the data volume that exists, and same-language
same-period (which flatters it), the ceiling is ~7% exact and ~55% within two
segments. Any claim about a specific Xiongnu reconstruction must live inside that.

---

## 11. Reading-anchored channel: coverage solved, transfer not (2026-08-26)

Step 10 forced this: at 1.4 observations per character a character-keyed channel
cannot be estimated. Step 11 keys the emission on the character's reconstructed
**Later Han reading** decomposed into (initial, vowel, coda), backing off
full reading -> (initial, vowel) -> initial -> global.

### Coverage - solved

| level | Xiongnu characters | cumulative |
|---|---|---|
| character seen directly in training | 31 (38.3%) | 38.3% |
| full reading seen | 17 (21.0%) | 59.3% |
| initial+vowel seen | 14 (17.3%) | 76.5% |
| initial seen | 19 (23.5%) | **100.0%** |

A character-keyed channel reaches 38.3% of Xiongnu characters. Reading-anchored
with backoff reaches **100%**. The structural block is gone.

### In-domain accuracy - large gain

Same 858 Sanskrit training pairs, held-out Sanskrit test:

| architecture | exact | within1 | within2 | mean ned |
|---|---|---|---|---|
| character-keyed, syllable units | 8.2% | 17.4% | 32.8% | 0.410 |
| character-keyed, segmental units | 8.8% | 22.5% | 39.2% | 0.437 |
| **reading-anchored, segmental** | **25.0%** | **57.9%** | **77.0%** | **0.224** |

**+16.2 points on exact match, a 2.8x improvement**, at unchanged data volume.
Position top-1 rose 32.6% -> 46.3%. Against step 10's curve this is worth roughly
a 5-8x increase in training data.

### Out-of-domain - and this is what kills it

The Sanskrit test set is in-domain: same period, same source language, same
conventionalised Buddhist practice. The Xiongnu material shares none of that.
Measured on the Ming Uyghur pairs with the same model:

| | position top-1 | exact | within2 | mean ned |
|---|---|---|---|---|
| in-domain (Sanskrit) | 46.3% | 25.0% | 77.0% | 0.224 |
| **out-of-domain (Uyghur)** | **9.8%** | **3.1%** | **27.5%** | **0.626** |

Position accuracy collapses from 46.3% to 9.8%. Fine-grained reconstruction does
not transfer across source language and period.

**Methodological note: the gate was initially set on the in-domain figure, which
would have passed and printed a full table of Xiongnu reconstructions.** Those
outputs looked superficially plausible (撑犁 -> ara/kara/tara against a proposed
tengri) and were noise. The gate now uses the out-of-domain figure, which is the
only one the Xiongnu names inherit.

### What transfers and what does not

Reconcile this with the earlier transfer test, which found Turkic transfer at
+0.42 over a random-repairing null (p<0.005). Both results are correct because
they measure different grains:

- **Coarse phonetic information TRANSFERS.** Onset place of articulation is
  physics, not convention, so a Sanskrit-derived compatibility model predicts
  Turkic onsets well above chance.
- **Fine-grained segment identity DOES NOT.** Chunk preferences are
  language-specific and convention-specific; a channel fitted to Buddhist
  Sanskrit practice has no purchase on ad-hoc Han-era Turkic transcription.

### Consequence for the deliverable

Full pronunciation reconstruction of the Xiongnu names is not supportable. What
is supportable is **coarse onset-level constraint** - "the first syllable of 撑犁
began with a dental or velar stop" - at roughly 65-80% reliability. That is a
narrower claim, and it is the one a historical linguist actually wants from a
machine: constrain the hypothesis space, do not pretend to resolve it.

Fixing the transfer gap would need Han-era Chinese transcriptions of a
NON-Indic language in quantity. Those do not exist: Sogdian in Chinese is ~35
Tang-era names, and the Xiongnu corpus is the unknown itself. This is a genuine
dead end for fine-grained reconstruction, not a gap awaiting effort.

---

## 12-13. In-domain Turkic training: the diagnosis confirmed (2026-08-26)

### Step 12 - the corpus

Ligeti (1966, 1969) published the Sino-Uyghur vocabulary with **no Chinese
characters** - the transcription is given in EFEO romanisation:

    qatir (ha-ti-eul) «mulet»      quping (hou-p'ing) «cruche»

That is a READING, which suits the reading-anchored architecture of step 11
exactly, since that keys on readings rather than characters. **594 unique pairs**,
217 distinct EFEO syllables, 1,736 tokens, **8.0 observations per syllable**.

Frequency validation: `eul`(118) = 兒 for final -r, `sseu`(61) = 思 for final -s,
`che`(69), `ti`(58), `ha`(83). The canonical Ming transcription inventory,
recovered from data.

**Four parsing traps, worth recording - fixing them doubled the yield 297 -> 594:**
1. EFEO aspiration uses a TYPOGRAPHIC apostrophe (U+2019), not ASCII.
2. Some EFEO forms contain a space: `(k'ou-eul-ha pan-ti)`.
3. Footnote digits sit between the closing paren and the gloss: `(k'ou-che)17 «`.
4. The Turkic form is often not at line start: `quru- «devenir sec»: qurudi
   (k'ou-lou-ti)`.

**And one upstream trap that cost half the pages:** journals print the article
title on recto and the AUTHOR NAME on verso, so a running-head filter must
include "ligeti" or every even page is silently dropped (84 pages kept -> 206).

### Step 13 - the result

Reading-anchored channel keyed on the EFEO syllable, backing off
full syllable -> (onset, rime) -> onset -> global. 499 train / 89 held out.
Held-out syllable OOV rate 5.6%, absorbed by the backoff.

| training -> test | exact | within1 | within2 | position top-1 |
|---|---|---|---|---|
| Sanskrit -> Turkic (step 11, out-of-domain) | 3.1% | 6.9% | 27.5% | 9.8% |
| Sanskrit -> Sanskrit (step 11, in-domain) | 25.0% | 57.9% | 77.0% | 46.3% |
| **Turkic -> Turkic (step 13, in-domain)** | **31.5%** | **57.3%** | **75.3%** | **45.4%** |

**+28.4 points on exact match over the out-of-domain baseline.** The step-11
diagnosis was correct: the collapse was about the training LANGUAGE, not the
method. A Chinese->Turkic transcription channel works.

Note it slightly EXCEEDS the Sanskrit in-domain figure on 594 pairs versus 858 -
because observations per unit is what matters and a reading inventory is closed,
where a character inventory is open.

### Residual error is partly corpus noise, not model error

Held-out samples:

    pou-eul-tch'a     gold burcaq      -> burca      (missing final q only)
    si-ti-eul pa-che  gold sitirbaS    -> sidirbas
    k'ouen-tou-sseu   gold kunduz      -> kuntuz     (voicing only)
    pou yin           gold buGil       -> buGil      EXACT

But some held-out pairs are extraction errors, not model failures:

    toryon            gold mangnuG     -> di, ti, tu
    mo-tch'e          gold it          -> mac, muc

`toryon`/`mangnuG` and `mo-tch'e`/`it` are mis-paired by the step-12 regex, so the
model is being scored against wrong gold. True performance is therefore somewhat
better than 31.5%. A length-ratio filter on the corpus would remove most of these.

### Where the project stands

The remaining gap to the Xiongnu names is **one problem instead of three**. It was
wrong period AND wrong source language AND wrong transcription convention. Steps
12-13 removed the last two. What remains is the ~1,200-year gap between Ming
Mandarin and Later Han - a single, testable question rather than a compound one.

---

## 14. The m-/b- probe (step 15)

**Question.** Ulug raised it: Turkic names should not begin with `m-`, so why would a Han
scribe reach for an `m-` character to write the founder's name 冒頓 (*mək-tuən)?

**Why it is answerable rather than speculative.** Reading 冒頓 as *baγatur requires the `m-`
to stand in for a `b-`. Proto-Turkic has no initial `*m-` at all — Old Turkic `m-` words are
loans, or come from `*b-` assimilating to a nasal directly after the vowel (*bän→men,
*buŋ→muŋ, *bin-→min-). So on the Turkic reading the substitution is load-bearing, not
incidental. And every corpus this project built is a set of transcriptions whose source word
is known, which turns "does that substitution happen?" into a counting exercise.

**Measurement.** `src/step15_initial_probe.py`, outputs in `reports/step15_summary.txt` and
`data/derived/initial_correspondence.csv`.

| corpus | source words in `b-` | written with a Chinese `m-` character |
|---|---|---|
| Mongolian (Secret History) | 738 | 0 |
| Turkic (Ligeti) | 78 | 0 |
| Sanskrit (Later Han, verified) | 22 | 3 |
| **total** | **838** | **3** (0.4%) |

Reverse direction, equally clean: Chinese `m-` renders a source `m-` in 303/305 Mongolian,
90/97 Sanskrit, 14/17 Turkic cases. The three Sanskrit exceptions are the only ones anywhere
in the collection and may be prenasalised `mb-` rather than plain `b-`.

**The decisive detail** is that scribes had a choice. Later Han had a voiced `b-` series
(並母) and used it: 239 of the Mongolian `b-` words took a `b-` character, 492 took `p-`.
Whoever wrote 冒 had the alternative and did not use it.

**Three ways out, in order of strain.**

1. The name is not Turkic. Yeniseian, para-Mongolic and Iranian all allow initial `m-`.
   Removes an obstacle; is not positive evidence for any of them.
2. Turkic with secondary `m-`. Attractive because *mək-**tuən** has a nasal in syllable 2 —
   but the assimilation does not reach that far. Counterexamples with a nasal at the same
   distance that keep `b-`: `bodun` "people", and `bıkın` "hip, flank" (Clauson, ref 4;
   pointed out by Ulug).
3. A loan or title rather than a native name. Dissolves the objection, but also dissolves the
   name's evidential value for the dynasty's language.

**Status of the claim.** This does NOT reconstruct the name — §5 of the paper stands, *mək-tuən
is a reading and not a reconstruction. What it does is put a number on a substitution that is
normally assumed in silence. Combined with the absent `-r` (step 14), there are now two
independent lines against *baγatur: one from the initial, one from the ending. Neither depends
on the channel model; both are counts over corpora anyone can recount.

**Trap avoided.** The first instinct was to answer this from general phonological knowledge.
The corpora make it a measurement instead, and the measurement is stronger than the argument
would have been — and, unlike the argument, it is falsifiable by recount.
