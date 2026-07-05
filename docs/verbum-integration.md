# TODO — wire Verbum (the wordplay lens) into the Lenses tab

**Status:** not built. Verbum's side is done and deployed-ready; this is the
Lectern-side consumer. Small change, one file.

## What Verbum is
The HOW-IT-SOUNDS lens — the Hebrew puns, name-plays, and sound-echoes the
English flattens (`adam`/`adamah`, `Babel`/`balal`, Isaac = laughter). Repo
`~/verbum`, intended prod `https://verbum.wrootpress.com`. Curated selection,
**not a complete Bible** — so, like Catena, link only where a play exists.

## The hook Verbum already exposes
Verbum emits a static manifest at **`/index.json`** — every play keyed by OSIS
refKey (the same join key the RCL spine / reception-corpus `osis` module use).
Shape (per play):

```json
{
  "edition": "genesis",
  "refKey": "Gen.2.7",
  "refDisplay": "Genesis 2:7",
  "book": "Genesis",
  "kind": "name",
  "kindLabel": "name",
  "heading": "The human and the humus",
  "contested": false,
  "anchor": "gen-2-7",
  "path": "/genesis#gen-2-7",
  "url": "https://verbum.wrootpress.com/genesis#gen-2-7",
  "start": { "osis": "Gen.2.7",  "book": "Gen", "chapter": 2, "verse": 7 },
  "end":   { "osis": "Gen.2.7",  "book": "Gen", "chapter": 2, "verse": 7 }
}
```

`start`/`end` are verse bounds (equal for a single-verse play, e.g. the range
play `Gen.2.25-Gen.3.1` gives start 2:25 / end 3:1). The reader honors the
`#anchor` fragment — scrolls to the play and flashes it — so `url` is a live
deep link.

## Where to add it
`src/connections.py`, function **`reading_links(refkey)`** — the same place
Catena/Topographia/Annales resolve. It returns `list[dict]`; whatever you append
flows automatically through `build_occasion.py` into the day's build JSON and
renders in the **Lenses tab** (`web/components/Workbench.tsx`). No web change
needed.

Add a `VERBUM = "https://verbum.wrootpress.com"` const and a helper that:
1. Loads the Verbum play index **once** (build-time, cached — mirror the lazy
   `_catena_cache` pattern).
2. For the day's reading (parse `refkey` via the `osis` module already imported
   here → book/chapter/verse range), finds plays whose `[start,end]` **overlaps**
   the reading's range — not just an exact single-verse equality (a play on
   Gen 2:23 should surface for a reading of Gen 2:18-25).
3. Emits one link per matching play (or a single "Wordplay" link to the first /
   best if you'd rather not stack several), label e.g.
   `"Wordplay — the human and the humus"` using `heading`/`kindLabel`, `url` from
   the manifest. Order it after Catena/Topographia/Annales, before Doctrine.

### Source of the index — decide (keep the no-dead-links discipline)
Two options, matching Lectern's "read each repo's own coverage" rule:
- **(A) Read the local repo at build time** — preferred, no network, source-first.
  Verbum should commit the manifest to a static file (ask: have `~/verbum` write
  `public/index.json` alongside the route, or read the built
  `~/verbum/.next/server/app/index.json.body`). Point Lectern at
  `Path.home() / "verbum" / ...`.
- **(B) Fetch the deployed `/index.json`** at build — simplest, but adds a network
  dep to Lectern's build and requires Verbum deployed first.

Recommend (A): add a committed `~/verbum/public/index.json` (one-line Verbum
change) and read it locally, exactly as Catena's `~/catena/data/*.json` is read.

## Overlap test (reference)
Reading `(book, ch_start, v_start, ch_end, v_end)` overlaps a play when
`play.start <= reading.end` **and** `play.end >= reading.start`, comparing
`(chapter, verse)` tuples (same book). The manifest gives you both endpoints
as `{chapter, verse}` so no re-parsing of refKeys is needed.

## Done when
- A Proper/occasion whose reading includes a Genesis play (e.g. any day with
  Gen 2 or the Babel narrative) shows a live "Wordplay" link in the Lenses tab.
- Days with no Verbum play show nothing (no dead link) — verified in the
  exported HTML, per the standing discipline.

## Note for the whole lens family
This manifest shape is intended to become the **shared lens→Lectern convention**.
When Catena and Voces emit the same `/index.json`, this same overlap-based
consumer generalizes — consider refactoring `reading_links` to iterate a list of
lens manifests rather than special-casing each.
