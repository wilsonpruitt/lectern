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
      "firstReading": { "ref": "Exodus 32:1-14", "refKey": "Exod.32.1-Exod.32.14",
        "refKeys": ["..."],   // OPTIONAL — every span of a split reading, copied from the RCL spine;
                              // the validator checks first-reading witnesses against all of them
        "doors": [ ... ]      // OPTIONAL — attested doors on the OT/Psalm reading, same shape as above
      }
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

**Status (2026-09-10, Phase 4b):** all 15 migrated cards now carry both tracks, and each card's *backfilled* track (the one v1 never wrote) has 2–3 attested first-reading doors. The track each card was originally written for still has `firstReading.doors: []`; filling those is open.

## `mode` — the copyright switch
- **`text`** — public domain (Catena Aurea Fathers, Wesley's Notes, Calvin, Luther…).
  `reading` may summarize or briefly quote the source.
- **`pointer`** — in-copyright (e.g. **Barth**). `reading` is **our own one-line
  gloss**; `cite` points to *where* the author treats it. The source's prose is
  **never stored or shown** — same posture as the hymn/Barth pointer rule. The UI
  marks these `cited` and shows the citation, not a quotation.

## How to author a card (Phase 4b brief)

The rule is unchanged: **never attribute from recall, only from a retrieved text.** What changed in
Phase 4b is that two sources are now required wherever the store has them, and the tooling checks you.

1. **Pull the witnesses.** `python3.11 src/turn_pull.py <occasion-id>` prints, from
   `~/reception-corpus`, every Glossa ordinaria (Migne) entry and every Wesley note on the Gospel and on
   each track's first reading and psalm, plus a count of everything else on file. It reads **every span**
   of a split reading from the RCL spine (`Gen 24:34-38, 42-49, 58-67` is three spans; the build only
   keys the first). Write the dump somewhere and read it before writing a word.
2. **Gospel doors (shared).** Keep 2–3 doors, each a different *landing*. Among them, cite **at least
   one Glossa ordinaria (Migne) witness and at least one Wesley witness** wherever the store has rows for
   them. Slot each into the door it actually supports; never bend a door to fit a witness.
3. **Per track.** For every track in `tracks`, write `gravity` and `synthesis` against *that track's*
   first reading and psalm (the second reading and Gospel are shared). Add 2–3 `firstReading.doors`
   where the attestation is real. Where Migne has no gloss on the book (Lamentations, Ezekiel, Daniel,
   the Twelve, Maccabees), Wesley plus Catena's intertextual notes can carry a door; if even that is
   thin, write fewer doors rather than stretching.
4. **Witness shapes** (the `work` string is what the UI keys on):
   ```jsonc
   {"author":"Glossa ordinaria","tradition":"medieval","work":"Glossa ordinaria (Migne)","mode":"text","reading":"..."}
   {"author":"John Wesley","tradition":"wesleyan","work":"Explanatory Notes","mode":"text","reading":"..."}
   {"author":"Catena — intertextual","tradition":"intertext","work":"Catena","mode":"text","reading":"... (taken up at Acts 18:5-6)"}
   ```
   The Migne `work` string is how the Turn tab tells the in-house Glossa apart from the Catena Aurea's
   second-hand "Gloss." fragments, which share the author name. It renders with a small "Migne" tag.
5. **`reading` is the source's own words**, lightly trimmed, never your gloss on them. Put your
   interpretation in `claim`, `say`, and `do`.
6. **Validate.** `python3.11 scripts/validate_turn.py [occasion-id]`. For Wesley, Migne Glossa, and
   intertext witnesses it checks that most of the reading's content words occur in that source's own rows
   on that passage. On the first Phase 4b card it caught an interpretive framing sentence that had slipped
   into a Wesley witness. Other authors are checked for attestation on the passage. A card with a missing track or a
   missing required source reports WARN; an ungrounded witness is an ERROR and exits 1.
7. Append to `_note` what you did and from what; keep `status: "draft"` until Wilson curates.

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
