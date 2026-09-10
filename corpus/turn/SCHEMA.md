# The Turn — schema + how to supplement it

The Turn reduces a pericope's abundance to **2–3 divergent focus drafts** ("doors"),
each a different *landing*, each grounded in **attested reading-traditions** — the
roads the church has actually walked. We *surface*, we do not author the doors.

**The load-bearing rule:** never attribute from recall — only from a *retrieved
text*. Every witness must trace to a row in the reception store
(`~/reception-corpus/data/reception.sqlite`), which is the single pluggable backend.

## Card schema — `corpus/turn/<occasion-id>.json` (v2, Phase 4a, 2026-09-10)

The **Gospel pericope and its doors are shared** across the day's tracks — a
Sunday is one Gospel reading no matter which OT/Psalm track a congregation is
following. What's genuinely per-track is the day's *nerve*: `gravity` and
`synthesis` were being written against whichever track's OT/Psalm reading was
actually vivid that week (verified card-by-card during the v1→v2 migration —
9 of the first 15 cards turned out to be written against **semicontinuous**,
not complementary, contrary to what an earlier draft of this doc assumed). So
those two move under `tracks.<key>`, alongside an optional set of **attested
doors on that track's own first reading** (OT/Psalm), which the Glossa's
whole-canon coverage (Phase 1) newly makes practical to source honestly.

An optional `"_note"` string (not shown above) carries the card's own provenance/process
history in plain prose — where its doors were pulled from, what's been revised and why,
including this migration. It's read by whoever authors or audits the card next; append to
it, don't replace it.

```jsonc
{
  "occasion": "proper-23-28-a",
  "pericope": "Matthew 22:1-14",
  "refKey":  "Matt.22.1-Matt.22.14",      // OSIS — the join key into reception
  "trap":    "...",   // the moralism it usually becomes (editorial)
  "hinge":   "...",   // the one unresolved offense (editorial)
  "doors": [                              // Gospel doors — SHARED across tracks
    {
      "landing": "Come clothed",          // the distinct emotional/theological landing
      "claim":   "...",                   // the one thing this door says
      "witnesses": [
        {
          "author":   "Gregory the Great",
          "tradition":"latin-patristic",  // canonical key (see TRADITION_LABEL)
          "work":     "Catena Aurea",
          "mode":     "text",             // "text" | "pointer"  (see below)
          "reading":  "...",              // grounded summary/short quote of the source
          "cite":     "CD II/2, 94"        // OPTIONAL — required for mode:"pointer"
        }
      ],
      "say": "...",  "do": "..."          // function: one thing to say + one to do
    }
  ],
  "tracks": {
    "complementary": {
      "firstReading": { "ref": "Isaiah 25:1-9", "refKey": "Isa.25.1-Isa.25.9", "doors": [] },
      "gravity":   "...",    // the day's nerve FOR THIS TRACK (editorial) — OMIT if not yet authored
      "synthesis": { "convergence": "...", "claim": "...", "here": "..." }   // OPTIONAL, editorial
    },
    "semicontinuous": {
      "firstReading": { "ref": "Exodus 32:1-14", "refKey": "Exod.32.1-Exod.32.14", "doors": [
        // OPTIONAL — attested doors on the OT/Psalm reading, same door shape as above.
        // Not yet authored on any migrated card; the mechanism is here for new cards.
      ] }
      // no "gravity" key at all = this track hasn't been authored yet. Workbench.tsx
      // shows "Not yet authored for this track" rather than hiding the tab or the toggle.
    }
    // Occasions with no dual tracks (Advent–Pentecost, festivals) use one key: "single".
  },
  "subtract": "...",                       // the doors are mutually exclusive — choose one
  "source":   "...",                       // provenance line
  "status":   "draft"                      // draft until Wilson curates
}
```

**`firstReading.doors` is empty on every card migrated from v1** (2026-09-10) — none of
the OT/Psalm attested doors existed before this schema, only the Gospel ones. Authoring
them, and the missing half of each migrated card's `gravity`/`synthesis`, is open —
see NOW.md.

## `mode` — the copyright switch
- **`text`** — public domain (Catena Aurea Fathers, Wesley's Notes, Calvin, Luther…).
  `reading` may summarize or briefly quote the source.
- **`pointer`** — in-copyright (e.g. **Barth**). `reading` is **our own one-line
  gloss**; `cite` points to *where* the author treats it. The source's prose is
  **never stored or shown** — same posture as the hymn/Barth pointer rule. The UI
  marks these `cited` and shows the citation, not a quotation.

## How to supplement (Barth · Luther · Philokalia · …)
The Turn does not hard-code its sources. To add one:

1. **Ingest it into the reception store** (`~/reception-corpus`) with its
   `source`, `author`, `tradition`, `work`, and `mode`. The store already holds
   latin/greek-patristic, medieval, Wesleyan, Reformed (Calvin), Puritan, 19th-c
   Protestant. Examples to add: Luther → `tradition:"reformation", mode:"text"`;
   Philokalia → `tradition:"eastern"` (theme-keyed, not verse-keyed — ingest as
   theme-tagged notes); Barth → `tradition:"modern", mode:"pointer"` (citation
   index only, no prose).
2. **See what's now available** for a pericope:
   `python3.11 src/turn_sources.py <refKey>` — lists every reception row grouped
   by tradition, including the newly-ingested source.
3. **Slot witnesses into the relevant door** (or open a new door if the source
   walks a genuinely different road). Add the tradition's display label to
   `TRADITION_LABEL` in both `src/turn_sources.py` and `web/components/Workbench.tsx`.
4. Re-bake: `python3.11 src/build_occasion.py --all`; rebuild `web`.

No schema change is needed to add a source — only data. That is the point.
