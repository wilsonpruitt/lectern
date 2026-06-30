# Hymn tagging — next-session plan

Goal: tag the **full UMH + The Faith We Sing corpus** against the frozen lexicon
(`data/tags/lexicon.json`, v1.1, 108 tags) so the tag-based connector
(`src/tag_connect.py`) lights up hymns for every Sunday — not just the 15-hymn
proof set. Readings (746/746) and Wesley sermons (155) are already tagged; hymns
are the last item set.

## Copyright posture (unchanged)
Pointer-only. We store: hymn **number + title + hymnal + our tags**. We do NOT
store lyrics or music. Hymnary's scripture/topic fields are **inputs that inform
our editorial tagging** against our own controlled vocabulary — we don't
republish hymnary's topic lists. (Same reasoning as the Barth pointer note in
`reference_data-repository-standard`: facts/citations are usable; expression is
not; our tags are our own.)

## Sources (verified 2026-06-30)
- **Roster:** `https://hymnary.org/hymnal/UMH` (~734 hymns, 9 paginated pages,
  ~120/page) and `https://hymnary.org/hymnal/FWS` (The Faith We Sing, 284 songs,
  #2000–2284). Each row = number + title/first-line (+ tune). Note numbers can
  carry letter suffixes (e.g. `121b`, `2257b`).
- **Per-hymn metadata:** `https://hymnary.org/hymn/UMH/<n>` and
  `https://hymnary.org/hymn/FWS/<n>` each expose a **Scripture** field and a
  **Topics** field. Example (UMH 136): Scripture "Psalm 23"; Topics "Providence;
  Adoration and Praise; Assurance; Comfort; Eternal Life; …".
- **Bulk topic lists (cheaper than per-hymn):** `https://hymnary.org/browse/topics/UMH`
  and `/browse/topics/FWS` — each hymnary topic links to the hymns under it.
- `hymnary.org/api/scripture?reference=...` works (returns hymns per passage) but
  is NOT scoped to UMH/FWS and gives no in-hymnal number — use the hymnal/hymn
  pages, not the API, for our roster.
- Our own **`data/umh_scripture_index.json`** already gives passage→UMH number
  for the Gospel/Psalm bulk (Gen–1 Cor 5) — a second, owned scripture source.

## Tagging approach — from metadata, not lyric OCR
Do NOT vision-OCR 1,000 pages of copyrighted lyrics. Tag each hymn from cheap
factual signals, against the frozen lexicon:
- **theme / function** ← hymnary **Topics** (crosswalk to our lexicon) + scripture.
- **image** ← the **title/first-line** is a strong signal ("The King of Love My
  Shepherd Is" → shepherd; "Come, Thou Fount" → water) + scripture.
- **mood** ← the agent's knowledge of well-known hymns + topic/genre cues.
For famous hymns the agent can tag all four facets confidently from
title + scripture + topics + general knowledge. Reserve a lyric read (from
Wilson's PDFs, transient) only for genuinely unfamiliar hymns.

## Pipeline (next session)
1. **Roster** — fetch the UMH + FWS hymnal list pages (use `curl` for raw HTML;
   WebFetch summarizes and won't dump all rows). Parse → `data/hymn_roster.json`:
   `[{hymnal, number, title}]`. Expect ~734 + 284 ≈ 1,018 entries.
   - This also FIXES the proof-set titles in `data/tags/hymn_tags.json`, which are
     from recall and unverified (e.g. confirm 136 vs 138 for "The Lord's My Shepherd").
2. **Enrich** — for each hymn, gather scripture refs + hymnary topics. Cheapest:
   scrape the ~few-hundred topic-browse pages once (topic → [hymn numbers]) rather
   than ~1,018 per-hymn fetches; fall back to per-hymn pages for stragglers.
   Politeness: cache raw to `cache/`, rate-limit, never re-fetch.
3. **Crosswalk** — build `data/tags/hymnary_topic_crosswalk.json`: hymnary topic →
   our lexicon tag(s). One-time editorial map (bounded; hymnary has a few hundred
   topics). This is curate-able and reusable.
4. **Tag** — parallel subagents (the proven pattern: frozen-lexicon leash, batches
   of ~90, structured JSON, `_proposed` for gaps), tagging from
   title + scripture + crosswalked topics. Merge → `data/tags/hymn_tags.json`
   (replace the 15-item proof set; keep its shape: `{hymnal, number, title,
   theme, image, mood, function}`).
5. **Validate** — `python3.11 src/validate_tags.py` (already validates hymns; must
   be 100% in-vocab). Spot-check a sample across hymnals/genres.
6. **Prove** — re-run `src/tag_connect.py` on several occasions across seasons;
   confirm rich, sensible recs (and fix the known Pentecost dual-track weighting
   if it still bites — see `out/proper-23-28-a-tag-recs.md`).

## Subagent prompt template (reuse from the RCL pass, adapted)
> Read the frozen lexicon `/Users/wilsonpruitt/lectern/data/tags/lexicon.json`
> (4 facets, closed vocab — use ONLY these exact keys) and the topic crosswalk
> `/Users/wilsonpruitt/lectern/data/tags/hymnary_topic_crosswalk.json`. For each
> hymn in your batch (given: hymnal, number, title, scripture, hymnary-topics),
> assign tags against the lexicon: theme 2–4, image 0–3 (from title + scripture;
> [] if abstract), mood 1–2, function 0–2. Use your knowledge of well-known
> hymns. Do not invent tags; copy keys verbatim; record genuine gaps in
> `_proposed`. Write JSON `{ "<hymnal> <number>": {theme,image,mood,function,
> title} }` to <output path>. Pointer-only — never store lyrics.

## Open decisions (defaults chosen; Wilson can override next session)
- **Roster + metadata from hymnary** (vs vision-OCR the PDF first-lines/topical
  indexes). DEFAULT: hymnary — clean, structured, has topics + scripture; PDFs
  stay the licensed books we point into. (PDF Topical index, pp. 934–954, remains
  a fallback/cross-check.)
- **Tag from metadata, not lyrics.** DEFAULT: yes (above).
- **Scope:** UMH + FWS both, full corpus. (Could stage UMH first if we want a
  faster first win.)
- **TFWS title verification:** the proof set has 1 TFWS hymn (2126); confirm its
  title against the FWS roster.

## Why this is the runway
Reading-side connection is done and proven. The only thing between us and
whole-year hymn recommendations is this corpus + a topic crosswalk — both
bounded, both copyright-safe, both fitting the proven parallel-tagging harness.
