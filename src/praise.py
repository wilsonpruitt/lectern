#!/usr/bin/env python3.11
"""Praise / contemporary worship song recommendations — Covenant UMC's own
repertoire (data/tags/praise_songs.json), connected to the day by shared faceted
tags, exactly like the hymns. POINTER-ONLY: we emit title + usage + connecting
tags + a lookup link; NEVER lyrics (most are copyrighted). Wilson curates the
tags (the thematic connections) in the songs file.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import quote_plus

import tag_connect as tc                       # WEIGHTS, tagset, score

LECTERN = Path(__file__).resolve().parent.parent
SONGS = LECTERN / "data" / "tags" / "praise_songs.json"

# Where "find the real song" points. YouTube search lands on the actual
# recordings; change this base if Covenant prefers SongSelect/etc.
def song_url(title: str) -> str:
    return f"https://www.youtube.com/results?search_query={quote_plus(title + ' worship song')}"


def load_songs() -> list[dict]:
    return json.loads(SONGS.read_text(encoding="utf-8"))["songs"]


def recommend(day_tags: set, songs: list[dict], top: int = 6) -> list[dict]:
    scored = []
    for s in songs:
        score, shared = tc.score(tc.tagset(s), day_tags, {})   # unweighted (small set)
        if score > 0:
            scored.append((score, s, shared))
    # tie-break by how often Covenant actually uses the song (their core repertoire)
    scored.sort(key=lambda x: (-x[0], -(x[1].get("timesUsed") or 0)))
    out = []
    for score, s, shared in scored[:top]:
        out.append({
            "title": s["title"],
            "timesUsed": s.get("timesUsed"),
            "frequency": s.get("frequency"),
            "pd": bool(s.get("pd")),
            "url": song_url(s["title"]),
            "tags": sorted(t for (_f, t) in shared),
            "score": round(score, 2),
        })
    return out
