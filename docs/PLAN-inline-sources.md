# PLAN — Glossa tab · Catena/Annales/Topographia inline · track-aware Turn

> **✅ Phase 1 DONE 2026-09-10 (Sonnet).** `~/reception-corpus/src/ingest_glossa.py` — 13,686
> rows / 55 books inserted as `source='glossa-ordinaria'`. Two real bugs found and fixed past
> what this section anticipated: a heading/block fallthrough bug that first produced zero rows,
> and the Vulgate-superscription verse shift (resolved per-chapter by a match-ratio oracle
> instead of a hand table — see the script's `resolve_psalm_offset`). Confirmed live via
> `turn_sources.available()`. Report gate: 80% overall lemma-match; low ratios on
> Sirach/Judith/Tobit/Esther (37–64%) are disclosed textual-tradition variance, not bugs — see
> NOW.md for the full note.
>
> **✅ Phase 2 DONE 2026-09-10 (Sonnet).** Glossa tab shipped beside Wesley's Notes —
> `src/glossa.py`, `build_occasion.py`'s `glossa`/`glossaBookCovered` fields, and
> `Workbench.tsx`'s `Glossa` component. Deviated from the plan in one place: some chunks mark
> the lemma with `«guillemets»` instead of `*asterisks*` (found during Phase 1's gate), so
> `glossMarkup()` renders both, not just asterisks. Clean `pnpm build`; both empty states
> verified against real occasions (Hosea for "book not in Migne", a John reading for "no
> comment on this passage").
>
> **✅ Phase 3 DONE 2026-09-10 (Sonnet).** Catena echoes, Annales chronology, and the
> Topographia map now render inline in the Lenses tab (`connections.py`'s `catena_echoes`
> / `annales_chronology` / `topographia_map`, `PlacesMapPanel`/`ChronologyPanel`/`EchoesPanel`
> in `Workbench.tsx`, `web/components/PlacesMap.tsx` for the Leaflet map). Real traps found
> past the plan's own warning: an Annales `ref` field can join several citations with " · "
> or name something non-biblical ("Kurkh Monolith (extra-biblical)"), and a handful of
> abbreviated book names (2 Chron, 1/2 Cor, 1 Thess) needed local expansion before
> `parse_citation` would accept them. All three builders ran clean across the full 1,253-
> reading corpus with zero crashes; clean `pnpm build`. Next: Phase 4 (track-aware Turn).

**Scoped 2026-09-10 (Fable). Executes in a cheaper session: Sonnet for phases 1–3 and the
schema half of 4; Opus for the authored Turn prose in 4b.** Everything below was read from the
repos on disk, not recalled. Where a fact must be re-verified at execution time it is marked ⚠.

## What Wilson asked for

1. The **Glossa ordinaria** — now fully Englished in `~/patrologia` — as a Workbench **tab like
   Wesley's Notes** (verse-by-verse on the day's readings), *and* as a **witness source for the
   Turn** alongside Wesley's Notes.
2. **Catena and Annales pulled into the site**, not linked out.
3. **Topographia inline when the passage has a map.**
4. **A Turn for each track** (semicontinuous and complementary), not one per Sunday.

## State of the sources (verified 2026-09-10)

| Source | Where | Shape | Rights |
|---|---|---|---|
| Glossa ordinaria, Migne recension | `~/patrologia/src/english/<idno>/NNNN.md` (Latin twin in `src/latin/`) | 60 texts, **866/866 chunks Englished**; `## CHAPTER N.` / `## PSALM N.` headings, `VERS. n.-- *lemma.* comment` entries, 14,743 `VERS.` addresses | In-house English, CC BY-NC per `wroot-press-licensing` |
| Wesley's Notes | already in `~/reception-corpus/data/reception.sqlite` (`source='wesley-notes'`, 17,920 rows) | verse-keyed | PD |
| Catena (NT echoes) | `~/catena/data/<slug>.json` — `pericopes[]{id,ch,ref,text,echoes[]}`; echoes carry `source, type, confidence, text, note` | 27 NT books | Own data, CC BY-SA 4.0 (`public/data/LICENSE.txt`) |
| Catena (OT → NT afterlife) | `~/catena/public/data/catena-fontium.json` — `sources[]{refKey, refDisplay, occurrences[]{refKey, refDisplay, slug, pericopeId, type, confidence}}`; `catena-readers.json` maps `Gen.1` → reader URL | OT/deutero | same |
| Annales | `~/annales-sacra/data/{divided-monarchy,life-of-paul}.json` (`spans[]{id,lane,label,group,start,end,ref,detail,note}`, `events[]{id,year,label,ref,kind,note,approx}`), `diatessaron.json` (`sections[]`, `episodes[]{id,section,title,refs:{matthew,mark,luke,john},note}`) | 3 editions | own |
| Topographia | `~/topographia-sacra/books/<slug>/chapters/N.json` (`title, places[], view{center,zoom}, route?, tribes?, verses[]{n,html}`), `books/<slug>/meta.json` (`built[]`), `data/gazetteer.json` (548 places: `name, coords[lat,lng], tier, id, appearances[]{book,chapter,verses[]}`) | Joshua, Judges, Ruth, Jonah, Acts | own; WEB text |

Reception store schema (unchanged, the pluggable backend):
`reception(refKey, refDisplay, book, chapter, v_start, v_end, source, author, tradition, work, text, provenanceUrl, mode, anchor)`.

---

## Phase 1 — Ingest the Glossa into the reception store  (Sonnet)

**New:** `~/reception-corpus/src/ingest_glossa.py`, modelled on `ingest_wesley_notes.py`
(read a sibling repo → rows → `INSERT`). One row per `VERS.` entry.

Row values:
- `source='glossa-ordinaria'`, `author='Glossa Ordinaria'`, `tradition='medieval'`, `mode='text'`,
  `work='Glossa ordinaria (Migne recension, PL 113–114)'` — the `work` string is what distinguishes
  these from the 316 second-hand `catena-aurea` rows whose author is also "Glossa Ordinaria"
  (their `work` is `Gloss.`/`Gloss. Ordinaria`).
- `refKey`/`book`/`chapter`/`v_start`/`v_end`: single verse per `VERS. n` address. Comment
  paragraphs that follow **without** their own `VERS.` line (a second lemma opening a paragraph,
  e.g. Ruth's `*Dip thy morsel.*`) attach to the current address.
- `text`: the English comment **with the lemma kept**, as `*lemma.* comment`. Keep the
  `*…*` italics markup (the tab renders italics; see Phase 2). Transform the note markup:
  `[n: (RAB.)]` → `(RAB.)` — the sigla are meaningful and the brief says they pass through;
  `[n: (Psal. CXVII)]` likewise → `(Psal. CXVII)`; `[var: …]` → drop; column markers
  `[0535B]` → strip from text, but keep the **first column seen for the address** as `anchor`
  so provenance can point at a column.
- `provenanceUrl`: the Patrologia work page for the idno (⚠ read the URL pattern from
  `~/patrologia/scripts/build-work-page.mjs`; `site/pl/<idno>/` is the likely shape).

Parsing rules (all observed in the corpus):
- Headings: `## CHAPTER II.`, `## CHAPTER II. (cont.)`, `## CHAPTER ONE.`, `## THE ONLY
  CHAPTER.` (→ 1), `## PSALM XXIII.`, `## PSALM XXIII. (cont.)`. Roman numerals. Argument /
  prologue / preface sections carry no verses — skip. Chapter state must **carry across chunk
  files in order** (a chunk can begin mid-chapter; frontmatter `heads` lists only the heads
  inside that chunk).
- `VERS. 3.--` arabic; the address is verbatim in the English.
- **Exclude** `9003` (a separate exposition on Ps 1–20, not the Glossa) and `9004` (the
  four-Gospel harmony, not verse-keyed to one book) from v1. Exclude `10724`/`10726`/`10727`
  (Anselm's own works in PL 162, not the recension — they have no chunk files anyway).
- Book map: Migne title → OSIS book. Traps: `Liber I/II Regum` = **1Sam/2Sam**, `III/IV Regum`
  = 1Kgs/2Kgs; `Paralipomenon` = Chr; `I Esdrae` = Ezra; deutero books (Tob, Jdt, Wis, Sir,
  Bar) use the OSIS codes the RCL spine already uses (⚠ check `osis.py` for the exact codes).
- **Psalms are Vulgate-numbered.** Convert to the Hebrew/OSIS numbering: Vulg 9 = Heb 9–10,
  Vulg 10–112 = Heb 11–113, Vulg 113 = Heb 114–115, Vulg 114–115 = Heb 116, Vulg 116–145 =
  Heb 117–146, Vulg 146–147 = Heb 147. The merged/split psalms need a verse offset too.
- **Vulgate verse numbering can differ from KJV/WEB** (superscriptions counted as v.1 in many
  Psalms; a few chapter splits elsewhere, e.g. Joel, Malachi, parts of the Song). Do **not**
  guess offsets by hand.

**Gate before the rows count as good (the wrong-gate rule: assert only what you're sure of):**
- `--report` mode prints, per book: chunks read, `VERS.` entries found, entries mapped, and a
  **lemma-match ratio** — for each entry, does the English lemma fuzzy-match the WEB/KJV text of
  the verse it was mapped to (WEB per-chapter text is in `~/catena/data/ot-chapters.json` and
  the NT book files; KJV in `~/kjv-wesley`)? A book whose ratio is well below its neighbours
  has a numbering offset. Fix the mapping, rerun, then insert. Psalms in particular must clear
  this ratio before insert.
- Spot-read 10 random rows per testament against the plate-facing Latin chunk.
- Run `python3.11 ~/lectern/src/turn_sources.py Matt.13.1-Matt.13.23` afterwards: the Glossa
  should now appear under Medieval with `work` = the Migne string. That is the whole test that
  the Turn can see it.

Coverage note for the tab's honesty line: the Migne recension is **abridged, marginal gloss
only (no interlinear), 58 of ~73 books**, misattributed to Walafrid Strabo; attributions
inside are unreliable. Every page that shows it says so (this is settled in `glossa-ordinaria.md`).

## Phase 2 — The Glossa tab  (Sonnet)

Mirror the Wesley's Notes plumbing exactly.

- `src/glossa.py` (copy of `src/wesley_notes.py` with `source='glossa-ordinaria'`), same
  cross-chapter span expansion via `rcl.chapter_query_spans`. Return `{chapter, v_start, v_end,
  text, anchor}`.
- `src/build_occasion.py::track_readings`: add `"glossa": gl.glosses_for_refkey(...)` beside
  `"notes"`. Flows into `data/build/*.json` and the mirrored `web/public/api/*.json`; add the
  field to `docs/API.md`.
- `web/lib/data.ts`: `Gloss` type; `Reading.glossa: Gloss[]`.
- `web/components/Workbench.tsx`: new `TabKey "glossa"`, label **"Glossa"**, placed in the same
  cluster directly after "Wesley's Notes". Component `Glossa` = copy of `Notes` with: the
  honesty intro line + "Read the full edition ↗" to `https://patrologia.wrootpress.com/glossa/`;
  per-reading groups; per-entry `v.n` + text. Render `*…*` as `<em>` with a 5-line splitter (no
  markdown library). Empty states: "The Glossa has no comment on this passage" / "Migne's
  recension does not include this book".
- Keep `notes` as the default tab. Size check after bake: `du -sh data/build` (was 9.4M).

## Phase 3 — Catena, Annales, Topographia inline  (Sonnet)

Design decision: **one Lenses tab, inline panels per reading**, not three new tabs. Each lens
keeps a small "open in Catena/Annales/Topographia ↗" link at the panel foot so the outbound
route still exists. `connections.reading_links` stays as-is for the link list; the new content
lives beside it.

`src/connections.py` gains three builders, all reading the sibling repos at build time (the
existing local-repo pattern; no network):

**3a. Catena → `echoes`**
- NT reading: every pericope in `~/catena/data/<slug>.json` whose verse range overlaps the
  reading (reuse `_catena_pericope_id`'s overlap loop but collect all, not first). Emit
  `{pericopeId, ref, echoes:[{source, type, confidence, text, note}]}`. Cap the inline list at
  the pericope's echoes sorted high→low confidence; do not truncate `note`.
- OT/deutero reading: from `catena-fontium.json`, sources whose `refKey` falls inside the
  reading range → `{source: refDisplay, occurrences:[{refDisplay, slug, pericopeId, type,
  confidence, url}]}` with `url = CATENA/<slug>#p-<pericopeId>`. Keep the chapter reader link.
- Render: per reading, a list of echoes with source ref, type badge, confidence, the quoted
  source text (WEB), and the note. Attribution line: "Catena, CC BY-SA 4.0".

**3b. Annales → `chronology`**
- Parse each span/event `ref` (and each `detail` when it is a citation) with
  reception-corpus's `parse_citation`. ⚠ **Normalize en dashes to hyphens first**:
  `parse_citation('Acts 7:54–8:1')` returns only `Acts.7.54`, while the hyphen form returns
  the full range (verified). A bare chapter ref (`1 Kings 12`) is the whole chapter.
- Overlap with the reading → `{edition, editionUrl, spans:[{label, group, lane, start, end,
  length, ref, note}], events:[{year, label, ref, kind, approx, note}]}`. Show consensus dates
  and say "dates per the Acts-based consensus" (the editions carry alternate `schemes`; ignore
  them in v1).
- Gospel readings → the Diatessaron: episodes whose `refs[<gospel>]` overlaps the reading →
  `{harmony:[{title, section, refs:{matthew,mark,luke,john}, note}]}`. The parallels are the
  payoff for a preacher ("also in Mark 4:1–9, Luke 8:4–8").
- Render: a compact "Where this sits" card per reading. No change needed in `~/annales-sacra`;
  the old note about adding `#span-id` scrolling there becomes optional.

**3c. Topographia → `map`** (only when the passage has one)
- Condition: `book in TOPO_SLUG` **and** chapter ∈ `books/<slug>/meta.json.built`.
- Places: gazetteer entries whose `appearances[]` include this book+chapter with a verse inside
  the reading's range; fall back to the chapter's `places[]` when the reading is a whole
  chapter. Emit `{chapterUrl, title, view:{center,zoom}, route?, places:[{key, name, coords,
  tier, id}]}`. Skip `tribes` polygons in v1 (Joshua 13–19 only; the GeoJSON is approximate).
  Multi-chapter readings → first built chapter, say so in the card.
- Web: `web/components/PlacesMap.tsx`, client-only (`next/dynamic`, `ssr:false`), Leaflet from
  cdnjs (pin the version; static export has no bundler step for CSS, so load Leaflet's CSS by
  `<link>` in the component), CARTO Voyager tiles with the same attribution string as
  `~/topographia-sacra/assets/chapter.js`. Pins by tier (identified / probable / conjectural /
  region) matching Topographia's colours; draw `route` as the dashed polyline. Call
  `map.invalidateSize()` after the panel mounts. Under the map, a plain list of places with
  tier and the one-line `id` — this is the no-JS/accessible fallback and is useful on its own.

Contract: `lenses.readings[i]` gains optional `echoes`, `chronology`, `map`; `docs/API.md`
lists them. Nothing in the `worship` block changes, so Circuit's drop-in is untouched.

## Phase 4 — Track-aware Turn, Glossa + Wesley as witnesses

**4a. Schema v2 (Sonnet).** Today a card is one Gospel pericope plus one `gravity` and one
`synthesis`, and the 16 existing cards' synthesis/gravity are written against the
**complementary** OT/Psalm (Proper 10-A cites Isaiah 55 and Psalm 65 — verified). New shape:

```jsonc
{
  "occasion": "...", "pericope": "...", "refKey": "...",   // Gospel — shared by both tracks
  "trap": "...", "hinge": "...", "doors": [...], "subtract": "...",
  "tracks": {
    "complementary":  { "gravity": "...", "synthesis": {...}, "firstReading": { "ref": "...", "refKey": "...", "doors": [...] } },
    "semicontinuous": { "gravity": "...", "synthesis": {...}, "firstReading": {...} }
  },
  // Sundays with no tracks (Advent–Pentecost, festivals): "tracks": { "single": {...} }
  "source": "...", "status": "draft"
}
```

- `firstReading.doors` is optional: attested doors on the OT/Psalm of **that** track,
  witnessed from the store (this closes the long-open "per-reading attested doors" item; the
  Glossa ingest is what makes it possible whole-canon).
- Migration script `scripts/migrate_turn_v2.py`: for each of the 16 cards, move `gravity` +
  `synthesis` under `tracks.complementary` (⚠ confirm per card by reading the synthesis against
  the two tracks' first readings in `data/build/<id>.json`; do not assume). `hasTurn` in
  `_index.json` stays true when either track has content; add `hasTurnTracks: [...]`.
- `build_occasion.load_turn` passes the new shape; `web/lib/data.ts` types follow;
  `Workbench` Turn tab reads `occ.turn.tracks[t.key] ?? occ.turn.tracks.single` so the existing
  semicontinuous/complementary toggle now switches the Turn too. Show a quiet "not yet
  authored for this track" line where a track is missing rather than hiding the tab.
- Update `corpus/turn/SCHEMA.md` and the `_note` convention.

**4b. Authoring (Opus — per `feedback_opus-for-authored-prose`).**
- Rewrite the authoring brief (`corpus/turn/SCHEMA.md` "how to author" section; the pull
  script lives in `scratchpad/turn_pull.py` and must be re-created if the scratchpad was
  cleared): for every card, run `turn_sources.available()` on the Gospel **and on each track's
  first reading**, and require, wherever the store has them, **at least one Glossa witness and
  one Wesley's Notes witness** among the Gospel doors — grounded in retrieved text, never
  recall (the load-bearing rule is unchanged). Label Glossa witnesses `work: "Glossa ordinaria
  (Migne)"` so the UI can distinguish them from Catena Aurea's second-hand Gloss. fragments.
- Backfill the 16 existing cards' `semicontinuous` half (gravity + synthesis; OT doors where
  the Glossa/Wesley attestation is real). Then both tracks for every new week going forward.
- `TRADITION_LABEL` needs no new key (medieval exists); add the Migne `work` string to the
  Workbench witness rendering so it prints "Glossa ordinaria (Migne)".

## Order, gates, and hard stops

1. Phase 1 → its `--report` gate → insert. (Everything else waits on this only for the
   Glossa tab and 4b; Phase 3 can run in parallel in the same session if RAM allows — it is
   file-reading, not agents.)
2. Phase 2 and Phase 3, `python3.11 src/build_occasion.py --all`, `pnpm build` in `web/`,
   check the built HTML for one tracked Sunday (Proper 10-A: Glossa on Matt 13 + Gen 25 + Isa
   55; echoes on Matt 13; Diatessaron parallels) and one map Sunday (an Easter-season Acts
   reading, or Proper 20-A Jonah 3).
3. Phase 4a, migrate, rebake, verify the toggle switches the Turn.
4. Phase 4b authoring.
5. **Deploy is a hard stop**: `./deploy.sh` is a production deploy; state it and wait for
   Wilson's per-action OK. Remember `--archive=tgz` is already in the script.

## Deliberately out of scope (say so, don't drift)

- Catena Aurea Fathers inline (they are in the store for Matthew only; they already surface
  as Turn witnesses).
- Tribal polygons, alternate Annales dating schemes, `#span-id` scrolling in Annales.
- 9003/9004 in the Glossa ingest; an interlinear/Rusch Glossa (Lane 2, deferred).
- Any change to the `worship` API block or the Circuit drop-in.
