# Call-to-Worship drafting brief (for batch generation)

You are drafting Call-to-Worship texts for **Lectern**, Wilson Pruitt's preacher's
workbench. Work in `/Users/wilsonpruitt/lectern`. These are **AI drafts pending
Wilson's curation** — but write them to the approved quality bar, not as filler.

## Read first (the quality bar)
1. `corpus/calls-to-worship/voice.md` — the house voice (read in full).
2. `corpus/calls-to-worship/registers.md` — the three registers A/B/C.
3. `corpus/calls-to-worship/drafts/proper-23-28-a.json` — the **APPROVED** example.
   Match its shape and quality exactly.

## For each occasion id (process in the given liturgical order)
1. **If `corpus/calls-to-worship/drafts/<id>.json` already exists, SKIP it.** Never overwrite.
2. Read `data/build/<id>.json` for the occasion name, season, and the day's
   readings (per track: role + ref + tags). **Lean on the Psalm and the Gospel**;
   the first reading and epistle feed images.
3. Draft **three registers**, all grounded in THIS day's readings:
   - **A — Spare:** 2–4 exchanges, **4–8 lines total**. House voice: short lines,
     concrete images, Scripture *woven not quoted/cited*, a gathering turn at the end.
   - **B — Immersive:** one **sensory anchor** drawn from the readings + a
     **building congregational refrain** that returns ~3–4×; warmer, expansive,
     pastoral; NOT bound by the 4–8 cap; still antiphonal; still ends with a turn.
   - **C — Hybrid:** A's economy (near 4–8 lines) + **exactly one** refrain + **one**
     sensory anchor.
4. Write `corpus/calls-to-worship/drafts/<id>.json` in EXACTLY this schema:
```json
{
  "_note": "AI-drafted Call to Worship — pending Wilson's curation.",
  "occasion": "<id>",
  "track": "complementary | semicontinuous | single",
  "registers": [
    {"key":"A","label":"Spare","desc":"house voice · 4–8 lines","lines":[["leader line","CONGREGATION RESPONSE"]]},
    {"key":"B","label":"Immersive","desc":"sensory anchor · building refrain","lines":[["",""]]},
    {"key":"C","label":"Hybrid","desc":"economy + one refrain","lines":[["",""]]}
  ]
}
```
   - `track`: dual-track days → `"complementary"`; single-track days → `"single"`.
   - Each line is a `[leader, response]` pair. The response is the congregation's
     answer (rendered bold downstream — do NOT add markdown/asterisks).
   - Plain UTF-8. Real text, never placeholders.

## Season refrain continuity
Within a run of consecutive Sundays in the same season, **reuse a season refrain**
in register B (and the single refrain in C), varying only the leader lines — the
way voice.md shows (Lent "pilgrims on the way"; Eastertide "Christ is risen,
Alleluia!"). Propose one fitting refrain per season-run and keep it. **Advent,
Lent, and Easter especially want sustained refrains.** Ordinary-Time propers are
more per-Sunday thematic — a season refrain is optional there.

## Avoid (AI-tells that betray the voice)
Stacked triads/parallelism, adjective pile-ups ("gracious, loving, ever-present"),
greeting-card abstraction ("on this beautiful morning"), over-explaining the move,
em-dash-and-summarize cadence, any citation/rubric/stage-direction inside the text.

## When done
Validate: from `/Users/wilsonpruitt/lectern` run
`python3.11 -c "import json,glob; [json.load(open(f)) for f in glob.glob('corpus/calls-to-worship/drafts/*.json')]; print('json ok')"`
