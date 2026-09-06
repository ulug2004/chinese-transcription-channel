# The Jie couplet: a pilot, and why it is not in this paper

**Scope decision, 6 September 2026: the present paper is long enough as it stands.
A second paper covers the reading of what is left, and this note is the first
item in it. The second paper's other announced contents are the Southern
Xiongnu succession, roughly nineteen chanyu the present record does not
contain, from 比 in 48 CE to 於扶羅 in 188 CE, together with the 尸逐 regnal
title series they carry. Both bodies of material are fourth century or later
and need the Early Middle Chinese values rather than the Later Han ones, which
is the same blocker in both cases.**

**Status: notes only. Nothing here is in the paper or the supplement, and nothing
here should go in until the four blockers in section 5 are cleared. If this work
continues it is a second paper, not a section of this one.**

Written 6 September 2026, after the 羯 row was reworked.

---

## 1. What the couplet is

The Jie left one surviving sentence. It is in the *Jin Shu* biography of the monk
Fotudeng, a prophecy given to Shi Le before his campaign against Liu Yao in 328:

```
秀支替戾岡，僕谷劬禿當
```

The *Jin Shu* glosses it element by element, in its own words:

```
秀支，軍也。          xiuzhi   = 軍   "army"
替戾岡，出也。        tiliegang = 出   "go out"
僕谷，劉曜胡位也。    puku     = Liu Yao's barbarian title
劬禿當，捉也。        qutudang = 捉   "capture"
```

That is the single most valuable property of this item and the reason it is worth
a second paper: **a Chinese transcription of a foreign utterance with a per-element
Chinese gloss.** It is the same evidential shape as 撑犁孤塗單于, which is the
calibration control of the present paper, but ten characters instead of six and a
sentence instead of a title.

## 2. The readings on record

| Author | Language | Segmentation and forms |
|---|---|---|
| Shiratori 1900, Ramstedt 1922 | Turkic | *sükä talıqın bügüg tutun*, on the *Jin Shu* segmentation |
| Bazin 1948 | Turkic | *süg tägti ıdqaŋ boquγıγ tutqaŋ* |
| Pulleyblank | (declined) | noted only that *-ŋ* is a frequent verbal ending in Yeniseian |
| Vovin 2000 | Yeniseian | 秀支 *suke*, 替戾岡 *thij-re(ts)-kang*, 僕谷 *bok-kok*, 劬禿當 *ko-thok-tang* |
| Shimunek, Beckwith et al. 2015 | Turkic | 秀 *su*, 支替戾岡 *kete-r erkan*, 僕谷 *boklug*, 劬禿當 *tukta-ŋ* |
| Vovin, Vajda, de la Vaissière 2016 | Yeniseian, revised | as Vovin 2000, argued closest to Pumpokol |
| Shervashidze | Iranian | not obtained |

Note that the two modern readings do not agree on where the words divide. Vovin
keeps the *Jin Shu*'s own four-way cut; Shimunek and Beckwith move 支 into the
second element.

## 3. What was actually computed

`price_engine.py` was run on each element, each reading scored on the segmentation
its own author proposes. 禿 (U+79BF) is absent from Schuessler's table and was
folded to 秃 (U+79C3) in the VARIANT map to make the run possible; that variant
pair is now in the engine and is used by nothing else.

Element by element:

```
秀支     suke        1 in 3        僕谷   bokkok    1 in 22
         süke        1 in 2               boklug    1 in 19
         süg         1 in 16              bügüg     1 in 50
                                          bokuğığ   1 in 168
替戾岡   tilekang    1 in 39       劬禿當 kotoktang 1 in 8,553
         talıkın     1 in 29,710          tuktang   1 in 2,199
支替戾岡 ketererkan  1 in 2,376           tutun     1 in 2,375,029
```

Whole couplet, all four elements multiplied:

```
Vovin 2000/2016, Yeniseian        1 in 26,176,425          best
Shimunek/Beckwith 2015, Turkic    1 in 239,552,204         9x
Ramstedt 1922, Turkic             1 in 7,902,309,486,573   301,887x
```

## 4. What those numbers do and do not mean

**They are not Yeniseian prices, and they are not Turkic prices.** The engine's
`SRCMAP` maps Turkish letters to Sanskrit phonemes and every rate comes from the
Sanskrit-to-Later-Han corpus. Fed `kotoktang` it read the letters as Turkish,
mapped *k* to Sanskrit {k, kh} and *t* to {t, th, ṭ, ṭh}, and priced those. Vovin's
Yeniseian never entered the calculation. The channel is language-agnostic and
cannot be otherwise.

So the number answers a narrower question than it appears to: **given that these
sounds stood behind the characters, how likely is this spelling.** That is a
legitimate way to compare hypotheses about *what sounds* a scribe heard. It is not
evidence about *which language* those sounds belong to.

The one sentence that survives all the caveats: **Ramstedt's 1922 reading is
300,000 times less likely than either modern reading**, on *talıkın* for 替戾岡
and *tutun* for 劬禿當. Nobody defends that reading, so this is confirmation, not
news. Between the two modern readings the gap is nine times on a four-element
string, which is nothing.

## 5. The four blockers

1. **No Yeniseian lexicon.** `data/derived` holds three word lists and all three
   are Turkic. The lexicon half of the method, which asks whether a reading is an
   attested word and which has retired more readings in this project than the
   channel has, cannot run on the Yeniseian side at all. Vovin's forms are taken
   on his authority. The comparison therefore switches off the harder test for
   one side only.

2. **Our Turkic lexicons cannot run it either.** They are Türk Dil Kurumu style
   indexes keyed on nouns and on infinitives in *-mak / -mek*. Checked directly:
   `sü` "army" is **not a headword**, nor are `ket`, `tut`, `teg`, `ıd`. The index
   has `sülemek`, `süñü`, `ıdmak` and twenty derivatives of `tutmak`, but not the
   bare stems the couplet needs. A null result on the Turkic side would be an
   artefact of the extraction, not a fact about Turkic.

3. **The period is wrong.** The channel is measured on Later Han material and the
   couplet is about 328 CE. Worse, Pulleyblank's Early Middle Chinese gives 支
   only as *tɕi*, never *kie*, and **every reading on the table, Turkic and
   Yeniseian alike, needs *ke* there.** On the right century's phonology the
   comparison may collapse or reorder.

4. **No morphology.** The engine prices sounds onto characters. *tukta-ŋ* is a
   stem plus a second-person imperative and *t-il-ek-ang* is four morphemes; the
   engine sees letters and no boundaries. Every name in the present paper is a
   noun or a title, so this limitation has never bitten before.

## 6. What to obtain, in order of what it buys

- **Heinrich Werner, *Vergleichendes Wörterbuch der Jenissej-Sprachen*, 3 vols.
  (Band 1: A–K, Band 2: L–Š, Band 3: Onomastik), Veröffentlichungen der Societas
  Uralo-Altaica 59, Harrassowitz, Wiesbaden 2002.** ISBN 3-447-04655-4. The
  standard comparative dictionary. Starostin's Yeniseian etymological database is
  free online and would serve for a first pass.
- **E. G. Pulleyblank, *Lexicon of Reconstructed Pronunciation in Early Middle
  Chinese, Late Middle Chinese, and Early Mandarin*, UBC Press, 1991.** For the
  ten characters at the right period.
- **Vovin, A., Vajda, E. & de la Vaissière, É. (2016), "Who were the *Kjet (羯)
  and what language did they speak?", *Journal Asiatique* 304.1.** The 2016
  restatement, with the earlier readings collected.
- Shervashidze's Iranian reading, not yet traced to a citation.

## 7. What to do first, and it helps the present paper too

**Rebuild the lexicon extraction to carry verb stems rather than Turkish
infinitives.** That is ours to do, needs nothing from a library, and blocker 2
above is not confined to the couplet: every frame search in the main paper that
needs a verb is weakened by it. Step 21 and the `dlt_lexicon.csv` builder are the
places to start. Do this before anything else here.
