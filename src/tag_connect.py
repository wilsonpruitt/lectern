#!/usr/bin/env python3.11
"""Lectern — connect hymns to the lectionary by SHARED TAGS (the robust index).

Where src/hymns.py joins on scripture coincidence (the printed index), this joins
on MEANING: each reading and each hymn carries faceted tags from lexicon.json;
a hymn is recommended when it shares tags with the day's readings. This is what
surfaces the non-standard connections the scripture index can't.

Still pointer-only: emits hymn number + title + the connecting tags.

Track-aware: the RCL's Pentecost dual tracks pull different directions, so recs
are computed per track (semicontinuous vs complementary).

Usage:
    python3.11 src/tag_connect.py proper-23-28-a
"""
from __future__ import annotations
import json, sys
from pathlib import Path

LECTERN = Path(__file__).resolve().parent.parent
TAGS = LECTERN / "data" / "tags"
SPINE = Path.home() / "reception-corpus" / "data" / "rcl.json"

# facet weights — image + theme carry the connection; mood/function are secondary
WEIGHTS = {"theme": 1.0, "image": 1.5, "mood": 0.6, "function": 0.5}


def load(p):
    return json.loads((TAGS / p).read_text(encoding="utf-8"))


def tagset(d):
    """{facet: [tags]} -> set of (facet, tag) pairs."""
    return {(f, t) for f in WEIGHTS for t in d.get(f, [])}


def occasion_tracks(occ, rcl_tags):
    """Group readings into tracks; return {track: {role: (refDisplay, tagset)}}.
    Untracked readings (psalm-less second/gospel) go into BOTH tracks."""
    tracks = {"semicontinuous": {}, "complementary": {}}
    shared = {}
    for r in occ["readings"]:
        if r.get("alt"):
            continue
        rk = r["refKey"]
        tags = tagset(rcl_tags["readings"].get(rk, {}))
        entry = (r["refDisplay"], tags)
        tr = r.get("track")
        if tr in tracks:
            tracks[tr][f"{r['role']}"] = entry
        else:
            shared[r["role"]] = entry
    for tr in tracks:
        tracks[tr].update(shared)
        if not any(t != "complementary" for t in [r.get("track") for r in occ["readings"]]):
            pass
    # if the day has no dual tracks at all, collapse to one
    has_tracks = any(r.get("track") for r in occ["readings"])
    if not has_tracks:
        return {"(single)": shared}
    return tracks


def score(hymn_tags, day_tags):
    shared = hymn_tags & day_tags
    s = sum(WEIGHTS[f] for (f, _t) in shared)
    return s, shared


def recommend(track_readings, hymns, top=6):
    day_tags = set().union(*[tg for (_d, tg) in track_readings.values()]) if track_readings else set()
    scored = []
    for h in hymns:
        ht = tagset(h)
        s, shared = score(ht, day_tags)
        if s > 0:
            scored.append((s, h, shared))
    scored.sort(key=lambda x: (-x[0], x[1]["number"]))
    return day_tags, scored[:top]


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: tag_connect.py <occasion-id>")
    occ_id = sys.argv[1]
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    occ = next((o for o in spine["occasions"] if o["id"] == occ_id), None)
    if not occ:
        sys.exit(f"no occasion {occ_id}")
    rcl_tags = load("rcl_tags.json")
    hymns = load("hymn_tags.json")["hymns"]

    print(f"# {occ.get('season','')} · {occ.get('name','')} ({occ['year']}) — tag-based hymn recs\n")
    tracks = occasion_tracks(occ, rcl_tags)
    for tr, readings in tracks.items():
        if not readings:
            continue
        print(f"## {tr} track")
        for role, (disp, _t) in readings.items():
            print(f"   {role}: {disp}")
        day_tags, recs = recommend(readings, hymns)
        if not recs:
            print("   (no tagged hymns share tags — widen the tagged hymn set)\n")
            continue
        print()
        for s, h, shared in recs:
            conn = ", ".join(sorted(f"{t}" for (_f, t) in shared))
            print(f"   {s:>4.1f}  {h['hymnal']} {h['number']}  {h['title']}")
            print(f"         via: {conn}")
        print()


if __name__ == "__main__":
    main()
