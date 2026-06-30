# The Turn — schema + how to supplement it

The Turn reduces a pericope's abundance to **2–3 divergent focus drafts** ("doors"),
each a different *landing*, each grounded in **attested reading-traditions** — the
roads the church has actually walked. We *surface*, we do not author the doors.

**The load-bearing rule:** never attribute from recall — only from a *retrieved
text*. Every witness must trace to a row in the reception store
(`~/reception-corpus/data/reception.sqlite`), which is the single pluggable backend.

## Card schema — `corpus/turn/<occasion-id>.json`
```jsonc
{
  "occasion": "proper-23-28-a",
  "pericope": "Matthew 22:1-14",
  "refKey":  "Matt.22.1-Matt.22.14",      // OSIS — the join key into reception
  "gravity": "...",   // the day's nerve (editorial)
  "trap":    "...",   // the moralism it usually becomes (editorial)
  "hinge":   "...",   // the one unresolved offense (editorial)
  "doors": [
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
  "subtract": "...",                       // the doors are mutually exclusive — choose one
  "source":   "...",                       // provenance line
  "status":   "draft"                      // draft until Wilson curates
}
```

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
