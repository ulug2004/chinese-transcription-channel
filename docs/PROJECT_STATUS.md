# Project status — steps 1–13

Reconstructing Turkic and other steppe names recorded in Chinese sources.
Every number below is measured, reproducible from `src/`, and logged in `reports/`.

Last updated 2026-08-26.

---

## The original question, and what happened to it

**Asked:** can the Chinese transcriptions of Xiongnu names be reversed to recover
the original pronunciation, and thereby the dynasty's language?

**Answer as it stands:** the *method* works, demonstrated on three languages. The
*Xiongnu application* is blocked by data density, quantified below. Language
attribution is not supportable on available reference data, and that is a
finding rather than a gap.

---

## Positive results

### 1. Separating transcription from calque (step 1)

The NTI/Fo Guang Shan dictionary mixes 音譯 (phonetic) with 意譯 (semantic):
釋迦牟尼 = *śākyamuni* vs 大乘 = *mahāyāna*. Training on calques poisons a channel.

Two approaches failed before one worked:
- character-set membership — bootstrapping swallowed common semantic characters
  (佛 天 王 生), after which everything scored 1.0 and 福慧 = *puṇya* slipped in
- character exclusivity — punished characters doing double duty, i.e. most of
  them; collapsed to 67 pairs

What worked: **phonetic verification** against Later Han readings. Align
characters to Sanskrit syllables, check each character's initial against its
syllable onset. 摩 \*mɑ / *ma* ✓, 慧 \*ɦuei / *ṇya* ✗.
**Result: 1,017 verified pairs.**

Independent validation — the akṣara inventory induced from scratch:

    k       ← 迦 俱 羯 伽 拘 緊 雞 計 髻 吉
    r       ← 羅 利 盧 囉 樓 蘭 留 洛 婁 勒
    (vowel) ← 阿 優 伊 鬱 鄔 烏 鴦 哩 一 盎

That is the standard Buddhist transcription character set, recovered without
being told it.

### 2. The channel generalises across corpora (step 4)

| test set | exact syllable top-1 | top-3 | onset top-1 |
|---|---|---|---|
| held-out Sanskrit | 62.1% | 89.6% | 84.0% |
| Baley Late Han (independent) | 46.4% | 73.2% | 79.6% |

### 3. Coarse phonetic information transfers cross-linguistically

Onset compatibility, Ming Uyghur, against a random-repairing null:

| | observed | null | lift | p |
|---|---|---|---|---|
| loose classes | 0.830 | 0.268 | +0.562 | <0.005 |
| tight classes | 0.740 | 0.159 | +0.581 | <0.005 |

Tightening the equivalence classes hurt the null more than the signal — the
signature of genuine correspondence rather than generous grouping.

### 4. A working Chinese→Turkic channel (steps 12–13)

| training → test | exact | within1 | within2 | position top-1 |
|---|---|---|---|---|
| Sanskrit → Turkic (out-of-domain) | 3.1% | 6.9% | 27.5% | 9.8% |
| Sanskrit → Sanskrit (in-domain) | 25.0% | 57.9% | 77.0% | 46.3% |
| **Turkic → Turkic (in-domain)** | **30.6%** | **68.2%** | **83.5%** | **48.9%** |

+27.5 points on exact over the out-of-domain baseline, on 563 pairs versus 858 —
because observations per unit is what matters and a reading inventory is closed
where a character inventory is open.

### 5. The channel works at scale (step 9)

Segmental channel on 9,329 Mongolian pairs, held out by whole chapters:

| | exact | within1 | within2 | mean ned |
|---|---|---|---|---|
| Sanskrit-trained, Baley | 8.2% | 17.4% | 32.8% | 0.410 |
| Secret History, unseen chapters | 36.9% | 66.3% | 87.5% | 0.150 |

---

## Negative results

### 6. Language attribution is not supportable (steps 5–6)

The Bayes-factor comparison failed its own controls: Ming Uyghur transcriptions
came out Turkic 8.6% of the time against a 16.7% chance floor.

A prior-ceiling diagnostic — handing the priors the TRUE source word, bypassing
Chinese entirely — showed the bottleneck is the prior, not the channel. Best
Turkic-vs-Yeniseian result anywhere in a 24-cell experiment (2 model families ×
4 length strata × 2 hypothesis sets): **69% against 50% chance**. Two cells fell
*below* chance, meaning systematic bias rather than weakness.

Causes, most severe first:
1. Turkic, Mongolic and Tungusic are phonotactically near-identical. This is a
   fact about the languages, not a modelling gap.
2. ~half of ASJP Swadesh entries are monosyllables, where vowel harmony — the
   best Turkic/Yeniseian discriminator — is undefined.
3. Equalising corpora to 469 forms is necessary (otherwise thin data wins by
   producing flatter models) but leaves too little to estimate anything sharp.
4. ASJP's 41-symbol alphabet discards the detail that separates neighbours.

### 7. Observations per character is the binding variable (step 10)

| corpus | obs/char | exact | within2 |
|---|---|---|---|
| Mongolian, full | 60.8 | 36.4% | 89.3% |
| Mongolian, 4,000 pairs | 39.8 | 19.3% | 78.6% |
| Mongolian, 2,000 pairs | 23.8 | 13.5% | 70.6% |
| Mongolian, 500 pairs | 9.5 | 7.3% | 53.5% |
| Sanskrit, 858 pairs | 5.0 | 8.8% | 39.2% |
| **Xiongnu names + titles** | **1.4** | — | — |

The Sanskrit corpus is sparser per character than the *smallest* Mongolian
sample, because Buddhist transcription uses a sprawling character inventory
while the Secret History uses a tight conventionalised one. And at 1.4
observations per character a character-keyed channel cannot be estimated at all.

The **segmental architecture** contributed +0.6 points at Han-era volume —
essentially nothing. It removes an inventory ceiling but buys no accuracy.
**Reading-anchoring** contributed +16.2 points (8.8% → 25.0%) and lifted Xiongnu
character coverage from 38.3% to 100%.

---

## Corpora produced (neither previously existed)

| corpus | size | notes |
|---|---|---|
| `shm_transcription_pairs.csv` | 9,329 pairs | Secret History of the Mongols, Yuan |
| `ligeti_turkic_chinese_pairs.csv` | 594 pairs (563 clean) | Ligeti 1966/69, Ming Uyghur |
| `nti_transcription_pairs.csv` | 1,017 pairs | verified Buddhist Sanskrit |
| `uyghur_coda_characters.csv` | 173 chars | **Pulleyblank EMC readings**, otherwise print-only |

---

## Methodological traps worth publishing

1. **Verso pages carry the author name, recto the title.** A running-head filter
   with only the title silently drops half an article. 84 pages → 206.
2. **Mongolian FVS ONE (U+180B) after a character marks an ANNOTATION** on the
   next character in the Secret History edition; U+180C and U+FE00 mark real
   transcription characters. Reverse the rule and the corpus is garbage.
3. **EFEO aspiration uses U+2019, not ASCII apostrophe.** With three other
   pattern fixes this doubled Ligeti yield, 297 → 594.
4. **Schuessler's tables print 虚 撐 户 脱 禄 where the histories print
   虛 撑 戶 脫 祿.** Without Unihan variant resolution ~15% of lookups miss silently.
5. **Baley's file is tab-separated despite a `.csv` extension**, and is 409
   entries not the paper's 401.
6. **Gating on in-domain accuracy would have published noise.** Step 11 passed an
   in-domain gate and printed confident Xiongnu reconstructions (撑犁 → ara/kara);
   out-of-domain accuracy was 3.1%. The gate must use the number the target
   material actually inherits.
7. **Equalising prior corpus sizes is mandatory in model comparison.** Unequal
   sizes let the thinnest-data model win by being flatter.

---

### 8. The period gap, measured (step 14)

The Turkic channel is trained on Ming readings; the Xiongnu names are Later Han.
The Tan appendix gives 164 characters with Pulleyblank EMC, Ning Old Mandarin and
Schuessler Later Han — the same characters across three eras — so the gap is
measurable without Xiongnu gold. Leave-one-out majority prediction of the earlier
reading from the later one:

| Ming → Later Han | accuracy |
|---|---|
| initial | 79.3% |
| nucleus | 50.0% |
| coda, nasal | 99.2% |
| coda, stop | 57.8% (majority guess only) |

**Do not quote an aggregate coda figure.** The blend gives a flattering 87% that
means nothing, because this sample is 72% nasal-coda characters. Split by class
the cross-tab is unambiguous:

    OM coda × Later Han coda
              0     k     m     n     p     t     ŋ
       0      1    26     0     0     5    14     0
       m      0     0    15     0     0     0     0
       n      0     0     0    58     0     0     1
       ŋ      0     0     0     0     0     0    44

Nasals survive intact (117/118). Stops are irrecoverable — Old Mandarin merged
-p, -t and -k into zero coda, so **0/45 preserved**, and the best possible guess
is the majority class -k at 57.8%.

**Why step 13 worked anyway:** the Ming transcription system compensated for its
own coda loss by marking foreign finals with an extra *character* rather than a
coda — 兒 (`eul`) for -r, 思 (`sseu`) for -s. Those are the two most frequent
syllables in the Ligeti corpus (118 and 61). The information sits in the syllable
sequence, not the Chinese coda, and the period shift does not remove it.

**The boundary this establishes:** onset-level claims about Xiongnu names are
supportable (~79% across the gap, on top of 48.9% in-domain position accuracy).
Nasal finals carry. Stop finals do not carry at all. Nucleus at 50% is the
weakest link and caps whole-form work independently of the coda question.

---

## What remains

No single blocking question. The measurable gaps have been measured.

Not worth pursuing: Clauson as bulk data, Hú & Huáng (Ligeti supersedes it), Qí
Hóngtāo at current yield, the Berlin/Munich woodblock scans, Pulleyblank hunting.

---

## Suggested paper shape

Not "we determined the Xiongnu language" and not "we reconstructed the names".

> A reproducible transcription-channel method with a measured learning curve,
> validated in-domain on three languages; two new corpora; and a quantified
> demonstration that language attribution and whole-form reconstruction are
> unsupportable at Han-era data density.

Three results, all honest, none contingent on winning an argument. The field is
full of confident hand reconstructions with unstated uncertainty; measured
ceilings are the contribution it does not have.
