#!/usr/bin/env python3.11
"""Lectern — assemble the per-occasion data contract the static shell consumes.

This is the build-time glue between the generators (sermon_connect, tag_connect,
call_to_worship) and the Layout-A workbench shell. For one RCL occasion it emits
a single self-contained JSON at data/build/<occasion-id>.json with the shape:

    {
      "occasion": {id, name, year, season, note?},
      "tracks": {                       # "single" when the day has no dual tracks
        "<track>": {
          "label": str,
          "readings": [{role, ref, refKey, tags:{facet:[..]}}],
          "sermons":  [{title, author, text, tags:[..], score}],
          "hymns":    [{hymnal, number, title, tags:[..], score}]
        }, ...
      },
      "calls":  {track, registers:[{key,label,desc,lines:[[lead,resp],...]}]} | null,
      "turn":   null,                   # homiletical layer — not yet built
      "lenses": null                    # lens family hooks — not yet built
    }

All reads are from data the OTHER generators own (rcl spine, *_tags.json, the
curated calls drafts). This script WRITES ONLY to data/build/. Re-run anytime a
tag set is refreshed (e.g. when the hymn corpus finishes tagging) and the hymn
recs deepen automatically — no change here needed.

Usage:
    python3.11 src/build_occasion.py proper-23-28-a      # one occasion -> data/build/
    python3.11 src/build_occasion.py --all               # every occasion in the spine
    python3.11 src/build_occasion.py proper-23-28-a --stdout
"""
from __future__ import annotations
import json, sys
from pathlib import Path

import tag_connect as tc            # WEIGHTS, load, tagset, score, SPINE, TAGS
import sermon_connect as sc         # recommend (sermon variant)
import connections as conn          # reading_links / doctrine_links (interpretive layer)

LECTERN = Path(__file__).resolve().parent.parent
BUILD = LECTERN / "data" / "build"
CALLS = LECTERN / "corpus" / "calls-to-worship" / "drafts"
FACETS = list(tc.WEIGHTS)           # theme, image, mood, function


def reading_tags(rcl_tags: dict, refkey: str) -> dict:
    """{facet: [tags]} for a reading, restricted to the scored facets."""
    d = rcl_tags["readings"].get(refkey, {})
    return {f: list(d.get(f, [])) for f in FACETS if d.get(f)}


def track_readings(occ: dict, rcl_tags: dict) -> dict:
    """{track: [reading-dict]} mirroring tag_connect.occasion_tracks but keeping
    refKey + ordered, contract-shaped reading dicts. Untracked readings appear in
    both tracks; 'alt' (or-alternative) readings are dropped, as in the connector."""
    tracks: dict[str, list] = {"semicontinuous": [], "complementary": []}
    shared: list = []
    has_tracks = any(r.get("track") for r in occ["readings"])
    for r in occ["readings"]:
        if r.get("alt"):
            continue
        entry = {
            "role": r["role"],
            "ref": r["refDisplay"],
            "refKey": r["refKey"],
            "tags": reading_tags(rcl_tags, r["refKey"]),
        }
        tr = r.get("track")
        if tr in tracks:
            tracks[tr].append(entry)
        else:
            shared.append(entry)
    if not has_tracks:
        return {"single": shared}
    for tr in tracks:
        tracks[tr] = tracks[tr] + [dict(e) for e in shared]
    return tracks


def day_tagset(readings: list[dict]) -> set:
    """Union of (facet, tag) pairs across a track's readings."""
    out: set = set()
    for r in readings:
        for f, tags in r["tags"].items():
            for t in tags:
                out.add((f, t))
    return out


def sermon_recs(day_tags: set, sermons: dict, top: int = 6) -> list[dict]:
    # Sermons are scored UNWEIGHTED (empty idf -> tc.score defaults each tag to
    # 1.0). The IDF rarity weighting is calibrated on the hymn corpus; applying
    # it to sermons would silently change the already-approved sermon recs.
    scored = []
    for _sid, s in sermons.items():
        score, shared = tc.score(tc.tagset(s), day_tags, {})
        if score > 0:
            scored.append((score, s, shared))
    scored.sort(key=lambda x: (-x[0], x[1].get("title", "")))
    out = []
    for score, s, shared in scored[:top]:
        out.append({
            "title": s.get("title"),
            "author": s.get("author"),
            "text": s.get("refDisplay"),
            "tags": sorted(t for (_f, t) in shared),
            "score": round(score, 2),
        })
    return out


def hymn_recs(day_tags: set, hymns: list[dict], idf: dict, top: int = 6) -> list[dict]:
    scored = []
    for h in hymns:
        score, shared = tc.score(tc.tagset(h), day_tags, idf)
        if score > 0:
            scored.append((score, h, shared))
    scored.sort(key=lambda x: (-x[0], x[1].get("number", 0)))
    out = []
    for score, h, shared in scored[:top]:
        out.append({
            "hymnal": h.get("hymnal"),
            "number": h.get("number"),
            "title": h.get("title"),
            "tags": sorted(t for (_f, t) in shared),
            "score": round(score, 2),
        })
    return out


def load_calls(occ_id: str) -> dict | None:
    f = CALLS / f"{occ_id}.json"
    if not f.exists():
        return None
    blob = json.loads(f.read_text(encoding="utf-8"))
    return {"track": blob.get("track"), "registers": blob.get("registers", [])}


def build(occ: dict, rcl_tags: dict, sermons: dict, hymns: list[dict],
          hymn_idf: dict) -> dict:
    tracks_in = track_readings(occ, rcl_tags)
    labels = {"semicontinuous": "Semicontinuous", "complementary": "Complementary",
              "single": "Readings"}
    tracks_out = {}
    for tr, readings in tracks_in.items():
        if not readings:
            continue
        dts = day_tagset(readings)
        day_themes = {t for (f, t) in dts if f == "theme"}
        tracks_out[tr] = {
            "label": labels.get(tr, tr),
            "readings": readings,
            "sermons": sermon_recs(dts, sermons),
            "hymns": hymn_recs(dts, hymns, hymn_idf),
            "lenses": {
                "readings": [
                    {"role": r["role"], "ref": r["ref"], "refKey": r["refKey"],
                     "links": conn.reading_links(r["refKey"])}
                    for r in readings
                ],
                "doctrine": conn.doctrine_links(day_themes),
                "social": conn.social_principles_links(day_themes),
            },
        }
    return {
        "occasion": {
            "id": occ["id"], "name": occ.get("name"),
            "year": occ["year"], "season": occ.get("season"),
        },
        "tracks": tracks_out,
        "calls": load_calls(occ["id"]),
        "turn": None,
        "lenses": None,
    }


def main() -> None:
    args = sys.argv[1:]
    if not args:
        sys.exit("usage: build_occasion.py <occasion-id> | --all  [--stdout]")
    to_stdout = "--stdout" in args
    args = [a for a in args if a != "--stdout"]

    spine = json.loads(tc.SPINE.read_text(encoding="utf-8"))
    rcl_tags = tc.load("rcl_tags.json")
    sermons = tc.load("sermon_tags.json")["sermons"]
    hymns = tc.load("hymn_tags.json")["hymns"]
    hymn_idf = tc.idf_weights(hymns)   # IDF over the hymn corpus (per tag_connect)

    if args == ["--all"]:
        targets = spine["occasions"]
    else:
        targets = [o for o in spine["occasions"] if o["id"] in args]
        missing = set(args) - {o["id"] for o in targets}
        if missing:
            sys.exit(f"no such occasion(s): {', '.join(sorted(missing))}")

    BUILD.mkdir(parents=True, exist_ok=True)
    n_calls = 0
    index = []
    for occ in targets:
        doc = build(occ, rcl_tags, sermons, hymns, hymn_idf)
        if doc["calls"]:
            n_calls += 1
        # ordered index entry (spine order is liturgical) for nav + the year view
        first_track = next(iter(doc["tracks"].values()), {"readings": []})
        index.append({
            "id": doc["occasion"]["id"],
            "name": doc["occasion"]["name"],
            "year": doc["occasion"]["year"],
            "season": doc["occasion"]["season"],
            "trackKeys": list(doc["tracks"].keys()),
            "readings": [{"role": r["role"], "ref": r["ref"]}
                         for r in first_track["readings"]],
            "hasCalls": bool(doc["calls"]),
        })
        if to_stdout and len(targets) == 1:
            print(json.dumps(doc, indent=2, ensure_ascii=False))
            continue
        out = BUILD / f"{occ['id']}.json"
        out.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    # Only (re)write the ordered index on a full build, so partial runs don't
    # truncate it. Filename starts with "_" so the web data layer skips it.
    if not to_stdout and args == ["--all"]:
        (BUILD / "_index.json").write_text(
            json.dumps({"occasions": index}, indent=2, ensure_ascii=False),
            encoding="utf-8")
    if not to_stdout:
        print(f"wrote {len(targets)} occasion file(s) to {BUILD}  "
              f"({n_calls} with curated calls)"
              + ("  + _index.json" if args == ['--all'] else ""))


if __name__ == "__main__":
    main()
