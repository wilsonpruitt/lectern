# Lectern

A preacher's / worship-planner's workbench over the church year. The lectionary
is a deck of series waiting to be dealt; Lectern works the whole liturgical
whole — text, meaning, and the things said aloud around the sermon.

This repo is the **standalone Lectern product**. Its first feature is the
**Call to Worship** generator.

## Call to Worship (first feature)

Spare, responsive, scripturally-informed calls to worship, keyed to the RCL and
written in the voice of the ones already in use at Covenant UMC Austin.

- **`corpus/calls-to-worship/circuit-corpus.json`** — the style corpus: 20 of
  Wilson's own calls to worship (and greetings), pulled from Circuit worship
  planning, 2026-06-30. This is the *voicing* source.
- **`corpus/calls-to-worship/voice.md`** — the voice spec distilled from the
  corpus: form (antiphonal, 3–6 exchanges, gathering turn), diction (spare,
  contemporary, concrete), scriptural grounding (weave, don't quote), and
  season-as-spine with sustained refrains.
- **`src/call_to_worship.py`** — the deterministic half of the pipeline. Given
  an RCL occasion id, it reads the **shared RCL spine in `~/reception-corpus`**
  (228 occasions — the data hub; this repo does not fork the spine) and emits
  the draft bundle (season + that day's readings). The generative half drafts
  the call from that bundle + `voice.md`.
- **`corpus/calls-to-worship/registers.md`** — three registers drafted per
  Sunday from the same readings: **A** spare (house voice), **B** immersive
  (Marcia McFee style — sensory anchor + building refrain), **C** hybrid.
- **`out/`** — worked drafts. `out/proper-23-28-a.md` is the proof-of-feel
  example (the banquet: Isa 25 / Ps 23 / Matt 22), all three registers.

### Usage

```sh
python3.11 src/call_to_worship.py --list "Lent"     # find occasion ids
python3.11 src/call_to_worship.py proper-23-28-a     # bundle for one Sunday
```

## Hymn recommendations (second feature)

Copyright-safe **pointer-only** hymn recs keyed to the lectionary: store and emit
hymn *numbers + hymnal* (facts), never lyrics or music.

- **`data/umh_scripture_index.json`** — the UMH *Index of Scripture: Hymns,
  Canticles, Prayers & Poems*, vision-OCR'd from Wilson's scanned copy
  (pp. 924-925). Each entry: `cite` (e.g. "Psalm 23") → `hymns` (UMH numbers).
  Coverage so far: Genesis–1 Corinthians 5; epistles tail + the Services/Psalter
  index + TFWS are a pending second OCR pass (see the file's `coverage` field).
- **`src/hymns.py`** — resolves each index citation to an OSIS refKey via
  reception-corpus's `parse_citation` (the *same* keys as the RCL spine, so the
  join is exact), then verse-range-overlaps the day's readings against the index.

```sh
python3.11 src/hymns.py proper-23-28-a
```

`out/proper-23-28-a-hymns.md` is the worked proof (Psalm 23 → UMH 128/136/137/
138/518; Matt 22:1-14 → 427 via verse overlap).

**Sourcing = hybrid** (decided 2026-06-30): the PDF Scripture Index gives the
canonical UMH/TFWS `passage → in-hymnal number` backbone; **hymnary.org**
(`/api/scripture?reference=...`) is the planned enrichment for the non-standard
connections the print index omits.

## Tag layer — the robust index (third feature)

A faceted **controlled vocabulary** tagged onto both readings and hymns, so they
connect by *meaning* — surfacing the non-standard connections the printed
scripture index can't (still pointer-only: tags are our editorial metadata, no
lyrics stored).

Method (decided 2026-06-30): open-tag a slice of the RCL → consolidate into a
frozen lexicon → tag the rest + the hymns against it. Faceted across **theme /
image / mood / function**.

- **`data/tags/lexicon.json`** — the controlled vocabulary (v0 seed, from Year A
  Propers 22-25). Canonical term + definition per tag, four facets.
- **`data/tags/rcl_tags.json`** — reading tags keyed by OSIS refKey (reusable
  wherever a text recurs).
- **`data/tags/hymn_tags.json`** — hymn tags (number + title + tags; proof set).
- **`src/tag_connect.py`** — scores hymns by weighted shared-tag overlap with the
  day's readings, **track-aware** (Pentecost dual tracks scored separately).

```sh
python3.11 src/tag_connect.py proper-23-28-a
```

`out/proper-23-28-a-tag-recs.md` shows the win: UMH 339 "Come, Sinners, to the
Gospel Feast" recommends for this Sunday via shared feast/hospitality tags,
though the scripture index only ever linked it to Luke 14.

## Next: full hymn corpus

Readings (746/746) and Wesley sermons (155) are tagged; the hymn corpus is the
last item set. The plan to tag the full UMH + The Faith We Sing corpus against
the frozen lexicon — sources, copyright posture, pipeline, and the subagent
prompt template — is in **`docs/hymn-tagging-plan.md`**.

## Dependency

Reads `~/reception-corpus/data/rcl.json` (the shared RCL spine, Years A/B/C).
Keep that repo present. The spine is the single source of truth for what each
Sunday appoints; Lectern consumes it by occasion id.

## Status

Proof-of-feel stage: corpus captured, voice spec written, one occasion drafted.
Next (pending Wilson's reaction to the feel): automate drafting across occasions,
add season-refrain continuity for multi-Sunday runs, then the static-site shell.
