# Draft entries, held back from the supplement

Rows worked out but not yet written into `docsrc/s1_rows.py`, each with an open
question named at the end of its section. The file began with the ruling clan
name and now holds more than that; the filename is narrower than its contents.

**Contents**

1. The ruling clan name — 虛連題 (*Karındaş*) and 攣鞮 (*-rındaş*), from step 49
2. 虛閭權渠 (*Kalkan*), from step 50

---

# 1. The ruling clan name

**Not yet in the supplement.** These two are written out here so the reasoning
and the numbers are kept, and can be dropped into `docsrc/s1_rows.py` when the
open question at the end is settled. Nothing in `s1_rows.py`,
`author_proposals.csv` or the paper has been changed.

Source: step 49 (`src/step49_clanname.py`, `RUN-clanname.bat`), output in
`reports/step49_summary.txt`. The measurement it rests on is now §8.5 and
Table 10 of the paper.

---

## What the record has

The clan name appears twice, and the two forms share a core:

```
攣鞮        lyan te        Shiji, Hanshu        c. 94 BCE
虛連題      kʰɨɑ / hɨɑ  lianᴮ  de     Hou Hanshu   5th c. CE
```

攣 *lyan* and 連 *lian* are the same syllable; 鞮 *te* and 題 *de* differ only in
voicing and tone. So the record is really **[攣鞮]** against **[虛] + [連題]** —
one identical core, with 虛 standing in front of it in the longer form.

## What retires the present reading, *El-indi*

Two counts, both from the Later Han corpus.

| | |
|---|---|
| A Chinese *l-* writing a source syllable that begins with a vowel | **0 of 140** |
| What a Chinese *l-* does write | a source **r**, 177 of 200 (88.5%); a source **l**, 85 of 88 (96.6%) |

*el* is vowel-initial, so 攣 cannot write it. The entry's own phonetics field
already conceded the point — "no corpus shows that kind of metathesis" — and
this is the measurement behind that concession.

---

## Entry 1 — 虛連題 → **Karındaş**

*proposed_sense:* kinsmen, those of one womb

### Phonetics

虛 *hɨɑ* → *ka*: the second of the character's two Later Han readings. §8.5 of
the paper measures why that one and not the other: a Turkic back *q* is written
with an *h-* character 43 times in 66, 65.2%, while a front *k* takes an
aspirated character 31 times in 35. *karındaş* has back vowels throughout, so
its initial is a *q*. On the aspirated reading *kʰɨɑ* the same word costs
**1 in 235**, because a source plain *k* takes an aspirated character only 6
times in 220. The row therefore depends on Table 10 and should say so.

連 *lianᴮ* → *rın*: a source *r* written with a Chinese *l-* is 177 of 200,
88.5%, and the *-n* is on the page, which a source *-n* is in 77 of 93, 82.8%.

題 *de* → *daş*: a source *d* written with a Chinese *d-* is 105 of 123, 85.4%,
and the sibilant coda is unwritten, which Table 7 licenses at 27 of 36, 75%.

**The whole name costs 10.2%, about 1 in 9**, against the 1 in 37 that retires
*Baγatur* in §8.1. Nothing is inserted, nothing is discarded, and there is no
metathesis: three characters, three syllables, in order.

Only two words in the lexicons fit the frame at all — *karındaş* and *kırındı*,
"crumbs".

### Reason

*karındaş*, modern *kardeş*, is *karın* "womb" with the suffix *-daş*: those of
one womb, kinsmen. Kāşgarî glosses it *kardeş*. A ruling lineage naming itself
by kinship is an ordinary formation and needs no epithet argument, which is
what the present reading needed — its own entry says the reading "is driven by
the sense rather than by the transcription".

### What is not settled

- The *q* rate is measured on Ligeti's Ming glossary, not on Han material,
  because Sanskrit has no *q* at all. §8.5 states this and uses it as a
  cross-period bound, the same way Table 9 uses the front rounded vowel.
- The vowel of the second syllable is not separately measured; the open-vowel
  rate is used for it.
- 虛 is absent from Schuessler's table under its traditional form and present
  under the simplified 虚. Four other characters of the record are in the same
  position: 戶 撑 祿 脫. Until the lookup matches both forms, those five are
  silently dropped by any script keying on the simplified column.
- The relation to 攣鞮, which is the subject of the second entry and the reason
  neither is in the supplement yet.

---

## Entry 2 — 攣鞮 → **-rındaş**, a fragment rather than a word

*proposed_sense:* the last two syllables of the preceding, with the first lost

### Phonetics

The frame is a liquid + vowel + written nasal, then a dental + vowel. **No word
in the three lexicons fits it — zero of 9,343 headwords.**

The reason is structural rather than accidental. Old Turkic does not begin words
with a liquid: 64 headwords of 9,343 start with *l-* or *r-*, 0.7%, and every
real one is a loanword — *laal* "rubinus", *lahan* "baptisterium", *last*
"stupa", *layh* "dignus". (Several apparent entries in that list are English
words that leaked into the Irk Bitig extraction from its commentary, which is a
separate defect to clean.)

So this form cannot be read as a Turkic word at all. On the reading proposed
above it is *-rındaş*, the last two syllables of *karındaş*, with 攣 taking *rın*
and 鞮 taking *daş*.

### Reason

**The unreadability is itself the argument.** A genuine two-syllable Turkic name
could not have this shape, because no Turkic word starts with a liquid.
Something is missing from the front. The three-character form supplies exactly
what is missing and reads cleanly at 1 in 9. That is why the longer form is
treated here as the fuller record and the shorter one as a truncation of it.

### What is not settled — and this is the objection to answer first

**The chronology runs the wrong way.** The Shiji is about 94 BCE. The Hou Hanshu
is fifth century CE. The truncation account requires the later source, by five
hundred years, to preserve more of the name than the earlier one. That is not
impossible — different informants, different periods of contact, and Chinese
renderings of foreign names are truncated elsewhere — but it is an assumption
running against the dates, and it is the reason these two entries are held here
rather than written into S1.

Three ways it could resolve, none yet tested:

1. The two forms are variants of one name and the Hou Hanshu preserves a fuller
   tradition. This is the conventional view and the one the reading assumes.
2. 虛 is a separate element — a title or modifier — standing before a
   two-syllable clan name. In that case the clan name is the unreadable core and
   *karındaş* is wrong.
3. The two are different names for different things, and the identification is
   itself the error.

---

## Paste-ready, when the question above is settled

```python
"虛連題": (
 """虛 <i>hɨɑ</i> → <i>ka</i>: the second of the character's two Later Han readings, and §8.5 of the paper measures why that one. A Turkic back <i>q</i> is written with an <i>h-</i> character 43 times in 66, 65.2%, while a front <i>k</i> takes an aspirated character 31 times in 35; <i>karındaş</i> has back vowels throughout. On the aspirated reading <i>kʰɨɑ</i> the same word costs 1 in 235, so this row depends on Table 10. 連 <i>lianᴮ</i> → <i>rın</i>: a source <i>r</i> written with a Chinese <i>l-</i> is 177 of 200, 88.5%, and the <i>-n</i> is on the page, 77 of 93, 82.8%. 題 <i>de</i> → <i>daş</i>: a source <i>d</i> written with a Chinese <i>d-</i> is 105 of 123, 85.4%, with the sibilant coda unwritten, which Table 7 licenses at 75%. <b>The whole name costs 10.2%, about 1 in 9</b>, against the 1 in 37 that retires <i>Baγatur</i> in §8.1. Nothing is inserted, nothing discarded, no metathesis: three characters, three syllables, in order. Only two words in the lexicons fit the frame, this one and <i>kırındı</i>, "crumbs".""",
 """<b>Karındaş, "those of one womb", kinsmen.</b> The word is <i>karın</i> "womb" with the suffix <i>-daş</i>, and Kāşgarî glosses it <i>kardeş</i>. A ruling lineage naming itself by kinship is an ordinary formation and needs no epithet argument, which is what the reading it replaces needed: that entry said in its own words that it was "driven by the sense rather than by the transcription". <b>What is not settled.</b> The <i>q</i> rate is measured on Ligeti's Ming glossary rather than on Han material, because Sanskrit has no <i>q</i>; §8.5 uses it as a cross-period bound in the same way Table 9 uses the front rounded vowel. The vowel of the second syllable is not separately measured. 虛 is absent from Schuessler's table under its traditional form and present under the simplified 虚. And the relation to <span class="han">攣鞮</span> is an inference, set out in that entry."""),

"攣鞮": (
 """攣 <i>lyan</i> and 鞮 <i>te</i> are the same two syllables as 連題 in the longer form of this name: 攣 and 連 are both <i>l</i> plus <i>ian</i>, and 鞮 and 題 differ only in voicing and tone. <b>No Turkic word fits the frame.</b> A liquid onset, a written nasal coda and a following dental returns zero of the 9,343 headwords in the three lexicons, and the reason is structural: Old Turkic does not begin words with a liquid. Only 64 headwords start with <i>l-</i> or <i>r-</i>, 0.7%, and every one is a loanword. <b>The reading this replaces is excluded outright.</b> <i>El-</i> is vowel-initial, and a Chinese <i>l-</i> character writing a vowel-initial source syllable is 0 of 140; 137 of those 140 took a glottal.""",
 """<b>Not a word, but the last two syllables of one.</b> On the reading proposed at <span class="han">虛連題</span> this is <i>-rındaş</i>, with 攣 taking <i>rın</i> and 鞮 taking <i>daş</i>, and the first syllable lost. <b>The unreadability is the argument.</b> A genuine two-syllable Turkic name could not have this shape, so something is missing from the front; the three-character form supplies exactly what is missing and reads at 1 in 9. <b>What is not settled, and it is the main objection.</b> The <i>Shiji</i> is about 94 BCE and the <i>Hou Hanshu</i> fifth century CE, so this account requires the later source, by five hundred years, to preserve more of the name than the earlier one. Chinese renderings of foreign names are truncated elsewhere, but the dates run against the account and it is recorded here as an assumption rather than a finding."""),
```

---
---

# 2. 虛閭權渠 → *Kalkan*

Source: step 50 (`src/step50_kalkan.py`, `RUN-kalkan.bat`), output in
`reports/step50_summary.txt`. **Nothing in the supplement has been changed.**
The row still reads *Kalkan*, "shield", exactly as before.

## What the entry currently says

> 虛 *kʰɨɑ* → *ka*, 閭 *liɑ* → *l*, 權 *gyan* → *kan*: the first three characters
> match exactly, including the written *-n* coda, at zero minority steps. Only
> 渠 *gɨɑ* is left unaccounted for, and it may carry a separate title element.

Step 50 finds one thing that helps it and two that do not.

## What helps: §8.5 puts it on the wrong branch of 虛

虛 is polyphonic, *kʰɨɑ* and *hɨɑ*, and *kalkan* has back vowels throughout, so
its velars are **q**. Table 10 of the paper measures a back *q* written with an
*h-* character at 65.2% and with an aspirated character at 30.3%. Pricing the
first three characters on each:

```
虛 = hɨɑ,  a source back q        14.44%    1 in 6
虛 = kʰɨɑ, a source plain k        0.60%    1 in 165
```

The entry is currently on the aspirated reading. On the *h-* reading the first
three characters are among the cheapest in the file. **That much is a clear
improvement and can be written in whatever else is decided.**

## What does not help, first: 渠 is not spare

The same character writes a **full syllable** elsewhere in this record — the
*ka* of *Çaka* at 且渠 — with its velar onset and open vowel doing real work.
Calling it "a separate title element" in this row and a syllable in that one
needs an argument, and the entry gives none.

## What does not help, second: an unaccounted character is not a licensed device

Of the 1,017 verified pairs, 152 (14.9%) use more characters than source
syllables. But that figure is two different things:

| | | |
|---|---|---|
| a Chinese **semantic suffix** appended | 77 | 舍衛大城 *śrāvastī*, 富單那鬼 *pūtana*, 迦樓羅鳥 *garuḍa*, 摩揭陀國 *magadha* |
| no obvious suffix, genuine phonetic expansion | 75 | 多他阿伽度 *tathāgata*, 窣路陀阿鉢囊 *srotaāpanna* |

The 77 are **category labels** — 鬼 demon, 鳥 bird, 國 country, 城 city — not
sounds. They cannot license an idle character in a personal name, because 渠 is
not a Chinese classifier.

## The frame search, which is the real problem

```
all four characters, four syllables         0
three syllables, 渠 left over               7    kalıtgan, karakan, kelegen, kerilgen,
                                                 kurulgan, kurıtgan, külergen
two syllables, 閭 gives only -l, 渠 idle     9    kalkan, kalkañ, kurgan "tumulus",
                                                 kelgin, kirkin, külgen, kılgan, kırkın
```

**No word in the lexicons uses all four characters.** The seven three-syllable
fits are all *-gAn* participles — the suffix step 47 established as productive —
but none of them reads as a ruler's name. And *kalkan* survives only if **two of
the four characters are nearly idle**: 閭 reduced to a bare *-l* with its vowel
writing nothing, and 渠 writing nothing at all.

## What is not settled

- No four-syllable word fits. If the name is one Turkic word, the frame is empty,
  which suggests the frame is wrong rather than the search.
- **The likeliest fix is that 虛閭權渠 is two elements, not one word.** 且渠 is a
  title in its own right in this same record, so 權渠 or 渠 alone may be a title
  following a name in 虛閭. That has not been tested.
- A character contributing only a coda consonant, as 閭 does here, is not
  measured anywhere as a licensed device. It should be, before the reading leans
  on it.
- 虛 is absent from Schuessler's table under its traditional form and present
  under the simplified 虚, with 戶 撑 祿 脫. Any script keying on the simplified
  column silently drops those five.

## Paste-ready, for the part that is settled

Only the onset correction is ready. The rest waits on the two-element test.

```python
# 虛閭權渠 — phonetics field, corrected onset only; the 渠 problem is NOT resolved
"""虛 <i>hɨɑ</i> → <i>ka</i>: the second of the character's two Later Han readings, which §8.5 of the paper selects: <i>kalkan</i> has back vowels, so its velars are <i>q</i>, and a Turkic back <i>q</i> is written with an <i>h-</i> character 43 times in 66, 65.2%, against 20 in 66 for an aspirated one. On the aspirated reading the same word costs 1 in 165; on this one the first three characters come to 14.4%, about 1 in 6. 閭 <i>liɑ</i> → <i>-l</i>, 權 <i>gyan</i> → <i>kan</i> with the <i>-n</i> written. <b>渠 remains unaccounted, and that is a real objection rather than a footnote.</b> The same character writes a full syllable elsewhere in this record, the <i>ka</i> of the reading proposed at 且渠, so it is not idle by nature. Nor does the corpus license leaving it idle: of the 152 pairs in 1,017 that use more characters than syllables, 77 are a Chinese semantic suffix appended to the transcription, 鬼 "demon", 鳥 "bird", 國 "country", and 渠 is not a classifier of that kind. No word in the lexicons uses all four characters."""
```
