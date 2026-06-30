#!/usr/bin/env python3.11
"""Connect Wesley SERMONS to a lectionary occasion by shared faceted tags — the
sermon sibling of tag_connect.py (hymns). For a given Sunday, surface the Wesley
sermons that resonate by MEANING (theme/image/mood/function), not just by citing
the same verse. Reuses tag_connect's scoring + track logic.

Usage:  python3.11 src/sermon_connect.py proper-23-28-a
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import tag_connect as tc   # WEIGHTS, load, tagset, occasion_tracks, score, SPINE

LECTERN = Path(__file__).resolve().parent.parent


def recommend(track_readings, sermons, top=6):
    day_tags = set().union(*[tg for (_d, tg) in track_readings.values()]) if track_readings else set()
    scored = []
    for sid, s in sermons.items():
        sc, shared = tc.score(tc.tagset(s), day_tags)
        if sc > 0:
            scored.append((sc, sid, s, shared))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return day_tags, scored[:top]


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: sermon_connect.py <occasion-id>")
    occ_id = sys.argv[1]
    spine = json.loads(tc.SPINE.read_text(encoding="utf-8"))
    occ = next((o for o in spine["occasions"] if o["id"] == occ_id), None)
    if not occ:
        sys.exit(f"no occasion {occ_id}")
    rcl_tags = tc.load("rcl_tags.json")
    sermons = tc.load("sermon_tags.json")["sermons"]

    print(f"# {occ.get('season','')} · {occ.get('name','')} ({occ['year']}) — Wesley sermon companion\n")
    print("Sermons connected to the day by shared faceted tags (lexicon v1), not scripture")
    print("coincidence. Score = Σ facet weights of shared tags (image 1.5 · theme 1.0 ·")
    print("mood 0.6 · function 0.5).\n")
    for tr, readings in tc.occasion_tracks(occ, rcl_tags).items():
        if not readings:
            continue
        print(f"## {tr} track")
        for role, (disp, _t) in readings.items():
            print(f"   {role}: {disp}")
        _day, recs = recommend(readings, sermons)
        print()
        if not recs:
            print("   (no tagged sermon shares tags with the day)\n")
            continue
        for sc, sid, s, shared in recs:
            conn = ", ".join(sorted(t for (_f, t) in shared))
            text = f"  · text: {s['refDisplay']}" if s.get("refDisplay") else ""
            print(f"   {sc:>4.1f}  {s['title']}  — {s['author']}{text}")
            print(f"         via: {conn}")
        print()


if __name__ == "__main__":
    main()
