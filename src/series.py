#!/usr/bin/env python3.11
"""Lectern's founding thesis: the lectionary is a deck of series waiting to be
dealt. This finds the NATIVE series — the runs the RCL already defines — by
walking the spine (liturgical order) and grouping consecutive occasions that read
the same book in a given role:

  - first reading (semicontinuous Track 1) — the OT lectio continua
  - second reading (Epistle) — runs continuously across both tracks
  - gospel — clusters where Matthew/Mark/Luke/John run a stretch

Each maximal run of >= MIN_RUN consecutive occasions sharing a book is a native
series. Computed from the spine alone — no editorial choices, zero risk. (Thematic
re-cuts, the curated non-contiguous series, are a separate tag-driven layer.)
"""
from __future__ import annotations
import json
import re
from pathlib import Path

SPINE = Path.home() / "reception-corpus" / "data" / "rcl.json"
NARRATIVES = Path(__file__).resolve().parent.parent / "corpus" / "series" / "narratives.json"
MIN_RUN = 3


def _narratives() -> dict:
    if NARRATIVES.exists():
        return {k: v for k, v in json.loads(NARRATIVES.read_text()).items()
                if not k.startswith("_")}
    return {}


def _beat_for(beats: list, week: int) -> dict | None:
    for b in beats or []:
        if b["from"] <= week <= b["to"]:
            return {"label": b["label"], "note": b.get("note")}
    return None

# OSIS book code -> display name (the books that actually run in the RCL tracks)
BOOK_NAME = {
    "Gen": "Genesis", "Exod": "Exodus", "Lev": "Leviticus", "Num": "Numbers",
    "Deut": "Deuteronomy", "Josh": "Joshua", "Judg": "Judges", "Ruth": "Ruth",
    "1Sam": "1 Samuel", "2Sam": "2 Samuel", "1Kgs": "1 Kings", "2Kgs": "2 Kings",
    "1Chr": "1 Chronicles", "2Chr": "2 Chronicles", "Job": "Job", "Ps": "Psalms",
    "Prov": "Proverbs", "Eccl": "Ecclesiastes", "Song": "Song of Songs",
    "Isa": "Isaiah", "Jer": "Jeremiah", "Lam": "Lamentations", "Ezek": "Ezekiel",
    "Dan": "Daniel", "Hos": "Hosea", "Joel": "Joel", "Amos": "Amos", "Jonah": "Jonah",
    "Mic": "Micah", "Hab": "Habakkuk", "Zeph": "Zephaniah", "Hag": "Haggai",
    "Zech": "Zechariah", "Mal": "Malachi",
    "Matt": "Matthew", "Mark": "Mark", "Luke": "Luke", "John": "John",
    "Acts": "Acts", "Rom": "Romans", "1Cor": "1 Corinthians", "2Cor": "2 Corinthians",
    "Gal": "Galatians", "Eph": "Ephesians", "Phil": "Philippians", "Col": "Colossians",
    "1Thess": "1 Thessalonians", "2Thess": "2 Thessalonians", "1Tim": "1 Timothy",
    "2Tim": "2 Timothy", "Titus": "Titus", "Phlm": "Philemon", "Heb": "Hebrews",
    "Jas": "James", "1Pet": "1 Peter", "2Pet": "2 Peter", "1John": "1 John",
    "Heb": "Hebrews", "Rev": "Revelation",
}

ROLE_LABEL = {"first": "First reading", "second": "Epistle", "gospel": "Gospel"}


def _book(refkey: str) -> str | None:
    m = re.match(r"([0-9A-Za-z]+)\.", refkey or "")
    return m.group(1) if m else None


def _reading(occ: dict, role: str) -> dict | None:
    """The reading for a role; for the first reading prefer the semicontinuous
    track (the lectio-continua line), else the plain reading."""
    cands = [r for r in occ["readings"] if r["role"] == role and not r.get("alt")]
    if not cands:
        return None
    if role == "first":
        semi = [r for r in cands if r.get("track") == "semicontinuous"]
        return semi[0] if semi else cands[0]
    return cands[0]


def native_series(occasions: list[dict]) -> list[dict]:
    """Maximal runs (>= MIN_RUN) of consecutive occasions sharing a book per role."""
    out = []
    for role in ("first", "second", "gospel"):
        run: list[tuple] = []  # (occ, book)

        def flush():
            if len(run) >= MIN_RUN:
                book = run[0][1]
                ids = [o["id"] for o, _ in run]
                out.append({
                    "role": role,
                    "roleLabel": ROLE_LABEL[role],
                    "book": BOOK_NAME.get(book, book),
                    "bookCode": book,
                    "weeks": len(run),
                    "occasions": ids,
                    "from": run[0][0].get("name"),
                    "to": run[-1][0].get("name"),
                })

        for occ in occasions:
            r = _reading(occ, role)
            bk = _book(r["refKey"]) if r else None
            if run and bk == run[-1][1]:
                run.append((occ, bk))
            else:
                flush()
                run = [(occ, bk)] if bk else []
        flush()
    # longest first
    out.sort(key=lambda s: -s["weeks"])
    return out


def build() -> dict:
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    by_year: dict[str, list] = {}
    for o in spine["occasions"]:
        by_year.setdefault(o["year"], []).append(o)
    narr = _narratives()
    out = {}
    for y, occs in by_year.items():
        series = native_series(occs)
        for s in series:                       # stable id + narrative arc/beats
            s["id"] = f"{y.lower()}-{s['role']}-{s['bookCode'].lower()}-{s['occasions'][0]}"
            n = narr.get(s["id"])
            if n:
                s["arc"] = n.get("arc")
                s["beats"] = n.get("beats", [])
        out[y] = series
    return out


def membership(series_by_year: dict) -> dict:
    """Per-occasion series membership: {occ_id: [{id, role, roleLabel, book, week,
    of, prev, next}]} — so the workbench can show 'week 3 of Romans' + step through."""
    mem: dict[str, list] = {}
    for series in series_by_year.values():
        for s in series:
            ids = s["occasions"]
            for i, oid in enumerate(ids):
                mem.setdefault(oid, []).append({
                    "id": s["id"], "role": s["role"], "roleLabel": s["roleLabel"],
                    "book": s["book"], "week": i + 1, "of": len(ids),
                    "prev": ids[i - 1] if i > 0 else None,
                    "next": ids[i + 1] if i < len(ids) - 1 else None,
                    "arc": s.get("arc"),
                    "beat": _beat_for(s.get("beats"), i + 1),
                })
    # within an occasion, show the longest series first
    for oid in mem:
        mem[oid].sort(key=lambda m: -m["of"])
    return mem


if __name__ == "__main__":
    for year, series in build().items():
        print(f"\n=== Year {year} — {len(series)} native series ===")
        for s in series:
            print(f"  [{s['roleLabel']:13}] {s['book']:16} {s['weeks']:2}wk  "
                  f"{s['from']} → {s['to']}")
