#!/usr/bin/env python3.11
"""Lectern — connect hymns to the lectionary by SHARED TAGS (the robust index).

Where src/hymns.py joins on scripture coincidence (the printed index), this joins
on MEANING: each reading and each hymn carries faceted tags from lexicon.json;
a hymn is recommended when it shares tags with the day's readings. This is what
surfaces the non-standard connections the scripture index can't.

Still pointer-only: emits hymn number + title + the connecting tags.

Track-aware: the RCL's Pentecost dual tracks pull different directions, so recs
are computed per track (semicontinuous vs complementary).

Two views:
  - default (aggregate): hymns that fit the WHOLE day (union of the track's
    readings). Good for "what shall we sing this Sunday."
  - --by-reading: hymns that fit EACH reading on its own. A single reading's
    distinctive tags (e.g. Rom 6's sanctification-holiness) get swamped in the
    aggregate; this view surfaces them for the preacher working that one text.

Usage:
    python3.11 src/tag_connect.py proper-23-28-a
    python3.11 src/tag_connect.py proper-8-13-a --by-reading
"""
from __future__ import annotations
import json, math, sys
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


def idf_weights(hymns):
    """Inverse document frequency over the hymn corpus: a tag held by many hymns
    is non-discriminating, so it counts less; a rare, distinctive tag (e.g.
    sanctification-holiness, held by ~26 hymns) counts much more. Returns
    {(facet, tag): idf}. Smoothed so a tag on every hymn still scores > 0."""
    n = len(hymns)
    df = {}
    for h in hymns:
        for ft in tagset(h):
            df[ft] = df.get(ft, 0) + 1
    # idf in (0,1]-ish range: log((N+1)/(df+1)) normalized by log(N+1)
    norm = math.log(n + 1)
    return {ft: math.log((n + 1) / (c + 1)) / norm for ft, c in df.items()}


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


def score(hymn_tags, day_tags, idf):
    shared = hymn_tags & day_tags
    s = sum(WEIGHTS[f] * idf.get((f, t), 1.0) for (f, t) in shared)
    return s, shared


def rank(day_tags, hymns, idf, top=6):
    scored = []
    for h in hymns:
        s, shared = score(tagset(h), day_tags, idf)
        if s > 0:
            scored.append((s, h, shared))
    scored.sort(key=lambda x: (-x[0], x[1]["number"]))
    return scored[:top]


def recommend(track_readings, hymns, idf, top=6):
    day_tags = set().union(*[tg for (_d, tg) in track_readings.values()]) if track_readings else set()
    return day_tags, rank(day_tags, hymns, idf, top)


def print_recs(recs, indent="   "):
    for s, h, shared in recs:
        conn = ", ".join(sorted(t for (_f, t) in shared))
        print(f"{indent}{s:>4.1f}  {h['hymnal']} {h['number']}  {h['title']}")
        print(f"{indent}      via: {conn}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    by_reading = "--by-reading" in sys.argv
    if not args:
        sys.exit("usage: tag_connect.py <occasion-id> [--by-reading]")
    occ_id = args[0]
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    occ = next((o for o in spine["occasions"] if o["id"] == occ_id), None)
    if not occ:
        sys.exit(f"no occasion {occ_id}")
    rcl_tags = load("rcl_tags.json")
    hymns = load("hymn_tags.json")["hymns"]
    idf = idf_weights(hymns)

    view = "per-reading" if by_reading else "whole-day"
    print(f"# {occ.get('season','')} · {occ.get('name','')} ({occ['year']}) — tag-based hymn recs ({view})\n")
    tracks = occasion_tracks(occ, rcl_tags)
    for tr, readings in tracks.items():
        if not readings:
            continue
        print(f"## {tr} track")
        for role, (disp, _t) in readings.items():
            print(f"   {role}: {disp}")
        print()
        if by_reading:
            # top hymns for EACH reading on its own — surfaces single-reading tags
            for role, (disp, rtags) in readings.items():
                recs = rank(rtags, hymns, idf, top=4)
                print(f"   ▸ {role} — {disp}")
                if recs:
                    print_recs(recs, indent="     ")
                else:
                    print("       (no tagged hymns share tags)")
                print()
        else:
            _day_tags, recs = recommend(readings, hymns, idf)
            if not recs:
                print("   (no tagged hymns share tags — widen the tagged hymn set)\n")
                continue
            print_recs(recs)
            print()


if __name__ == "__main__":
    main()
