#!/usr/bin/env python3.11
"""Migrate corpus/turn/*.json from v1 (one gravity/synthesis per card) to v2
(per-TRACK gravity/synthesis) -- Phase 4a of docs/PLAN-inline-sources.md.

v1 shape:  {..., "gravity", "synthesis", "doors" (Gospel), ...}
v2 shape:  {..., "doors" (Gospel, shared), "tracks": {"<track>": {"gravity",
            "synthesis", "firstReading": {"ref","refKey","doors":[]}}}, ...}

⚠ The plan's own assumption -- that all 16 (now 15) existing cards were written
against the COMPLEMENTARY first reading -- was verified per-card here and found
WRONG for most of them: 9 of 15 (the Genesis/Exodus narrative-arc stretch, Propers
13-19/21/22) are written against the SEMICONTINUOUS track instead, because that
track carried the more vivid narrative that week. Only 6 (Propers 9-12, 20, 23)
are genuinely complementary-anchored. This mapping was read by hand against each
card's own gravity/synthesis text and each track's actual first reading in
data/build/<id>.json -- not assumed. See docs/PLAN-inline-sources.md Phase 4a.

The OTHER track (whichever one the card was NOT written for) is left present with
a firstReading but no gravity/synthesis -- Workbench.tsx renders that as "not yet
authored for this track" rather than hiding the tab. Filling it in is Phase 4b
(Opus, authored prose).

Run: python3.11 scripts/migrate_turn_v2.py [--dry-run]
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TURN = ROOT / "corpus" / "turn"
BUILD = ROOT / "data" / "build"

# occasion id -> which track the v1 gravity/synthesis was actually written against,
# verified by reading each card's own text against both tracks' first readings.
WRITTEN_FOR = {
    "proper-9-14-a": "complementary",    # Zechariah 9 / Psalm 145 / Romans 7
    "proper-10-15-a": "complementary",   # Isaiah 55 / Psalm 65 / Romans 8
    "proper-11-16-a": "complementary",   # Wisdom 12 / Psalm 86 / Romans 8
    "proper-12-17-a": "complementary",   # 1 Kings 3 / Psalm 119 / Romans 8
    "proper-13-18-a": "semicontinuous",  # Genesis 32 (Jacob at the Jabbok)
    "proper-14-19-a": "semicontinuous",  # Genesis 37 (Joseph sold) / Psalm 105
    "proper-15-20-a": "semicontinuous",  # Genesis 45 (Joseph reveals himself)
    "proper-16-21-a": "semicontinuous",  # Exodus 1-2 (the midwives)
    "proper-17-22-a": "semicontinuous",  # Exodus 3 (the burning bush)
    "proper-18-23-a": "semicontinuous",  # Exodus 12 (Passover)
    "proper-19-24-a": "semicontinuous",  # Exodus 14 (the sea crossing)
    "proper-20-25-a": "complementary",   # Jonah 3-4
    "proper-21-26-a": "semicontinuous",  # Exodus 17 (water from the rock)
    "proper-22-27-a": "semicontinuous",  # Exodus 20 (the Ten Words)
    "proper-23-28-a": "complementary",   # Isaiah 25 / Psalm 23
}


def track_reading0(occ_id: str, track: str) -> dict | None:
    build = json.loads((BUILD / f"{occ_id}.json").read_text(encoding="utf-8"))
    t = build["tracks"].get(track)
    if not t or not t["readings"]:
        return None
    r = t["readings"][0]
    return {"ref": r["ref"], "refKey": r["refKey"], "doors": []}


def migrate_one(f: Path, dry_run: bool) -> None:
    occ_id = f.stem
    card = json.loads(f.read_text(encoding="utf-8"))
    if "tracks" in card:
        print(f"  {occ_id}: already v2, skipping")
        return
    written_for = WRITTEN_FOR.get(occ_id)
    if not written_for:
        print(f"  ⚠ {occ_id}: no WRITTEN_FOR mapping -- add one and rerun, not guessing")
        return

    gravity = card.pop("gravity", None)
    synthesis = card.pop("synthesis", None)
    tracks = {}
    for track in ("complementary", "semicontinuous"):
        fr = track_reading0(occ_id, track)
        if fr is None:
            continue  # this occasion doesn't have that track at all (shouldn't happen for these 15)
        entry = {"firstReading": fr}
        if track == written_for:
            entry["gravity"] = gravity
            entry["synthesis"] = synthesis
        tracks[track] = entry
    card["tracks"] = tracks
    card["_note"] = card.get("_note", "") + (
        f" [v2 migration 2026-09-10: gravity/synthesis moved under tracks.{written_for} "
        f"(verified against that track's first reading, not assumed); "
        f"the other track has firstReading only, pending Phase 4b authoring.]"
    )
    # key order: keep it readable -- occasion/pericope/refKey/trap/hinge/doors/tracks/subtract/source/status
    ordered = {}
    for k in ("_note", "occasion", "pericope", "refKey", "trap", "hinge", "doors"):
        if k in card:
            ordered[k] = card.pop(k)
    ordered["tracks"] = card.pop("tracks")
    for k in ("subtract", "source", "status"):
        if k in card:
            ordered[k] = card.pop(k)
    ordered.update(card)  # anything unanticipated, preserved rather than dropped

    print(f"  {occ_id}: gravity/synthesis -> tracks.{written_for}; "
          f"other track = {[t for t in tracks if t != written_for]}")
    if not dry_run:
        f.write_text(json.dumps(ordered, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    dry_run = "--dry-run" in sys.argv
    files = sorted(TURN.glob("*.json"))
    print(f"{'DRY RUN — ' if dry_run else ''}migrating {len(files)} cards")
    for f in files:
        migrate_one(f, dry_run)


if __name__ == "__main__":
    main()
