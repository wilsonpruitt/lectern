# Lectern API

Static, CORS-open JSON for consuming Lectern's lectionary data — built to drop a
Sunday's worship elements into **Circuit** (or any ChMS) with one fetch.

Base: `https://lectern.wrootpress.com/api`  ·  no auth  ·  `Access-Control-Allow-Origin: *`

## Endpoints
| URL | What |
|---|---|
| `/api/index.json` | Ordered list of occasions: `{id, name, year, season, date, display, hasCalls, hasTurn, series[], readings[]}`. Use to pick a Sunday. |
| `/api/{id}.json` | Full contract for one occasion + a flattened `worship` block (below). Beyond `worship`, each track's `readings[]` also carries `notes` (Wesley's Explanatory Notes) and `glossa` (the Glossa ordinaria, Migne recension) per reading — `[{chapter, v_start, v_end, text}]` (`glossa` entries also carry `anchor`, a PL column reference). Both are public-domain-or-in-house text, not pointer-only, but this doc's drop-in mapping below doesn't route them anywhere in Circuit yet. Each track's `lenses.readings[]` also carries `echoes` (Catena reception-history cross-references), `chronology` (Annales timeline/harmony placement), and `map` (a Topographia place list + view, only when that reading has a built map) — see `src/connections.py`'s `catena_echoes`/`annales_chronology`/`topographia_map` for the exact shapes; all three are `null` when nothing resolves. |
| `/api/series.json` | Native series per year (the RCL's lectio-continua runs). |
| `/api/manifest.json` | Self-describing manifest. |

Occasion ids look like `proper-9-14-a`, `resurrection-of-the-lord-a`, `first-sunday-of-advent-c`.

## The `worship` block — the easy drop-in
`/api/{id}.json` includes `worship`, a Circuit-friendly, flattened payload for the
primary track:

```jsonc
"worship": {
  "occasion": { "id", "name", "year", "season", "date", "display" },
  "track": "complementary",
  "callToWorship": {            // Wilson's own calls — 3 registers
    "track": "complementary",
    "registers": [ { "key": "A", "label": "Spare", "desc": "...",
                     "lines": [ ["leader line", "CONGREGATION RESPONSE"], ... ] }, ... ]
  },
  "scriptures": [ { "role": "first",  "ref": "Zechariah 9:9-12", "refKey": "Zech.9.9-Zech.9.12" }, ... ],
  "hymns":  [ { "hymnal": "UMH", "number": 367, "title": "...", "tags": [...], "score": 3.1 }, ... ],
  "praise": [ { "title": "This Is Amazing Grace", "timesUsed": 5, "frequency": "regular",
                "pd": false, "url": "https://...", "tags": [...], "score": 3.1 }, ... ]
}
```

Map these to Circuit `WorshipElement` rows:
- `callToWorship.registers[choose one].lines` → a `CALL_TO_WORSHIP` element (leader/response antiphon).
- each `scriptures[]` → a `SCRIPTURE` element (`ref` + `refKey`).
- each `hymns[]` → a `HYMN` element (hymnal + number + title).
- each `praise[]` → a `SONG` element (title + link).

## Pointer-only (copyright)
No copyrighted text is served — hymns/praise/sermons/confessions are **citations,
numbers, titles, tags, and links only**. Calls to worship and the Turn framing are
Lectern's own editorial content.

## Notes for the Circuit side (a separate build in `~/circuit`)
1. Fetch `/api/index.json`, find the occasion whose `date` matches the service date.
2. Fetch `/api/{id}.json`, read `worship`.
3. Let the planner pick a call register + which hymns/songs to insert, then create
   the `WorshipElement` rows. (Lectern only exposes the data; Circuit owns the insert.)
