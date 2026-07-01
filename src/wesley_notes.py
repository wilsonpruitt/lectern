#!/usr/bin/env python3.11
"""Lectern — John Wesley's Notes on the day's readings.

Replaces the old "Sermons tab" as the Workbench's primary Wesley resource:
Wesley wrote a note on nearly every verse of scripture (his *Explanatory Notes
Upon the Old and New Testament*), so his Notes companion the day's readings far
more directly than the sermon-recs did (those only connect by shared theme tag,
and only 155 sermons exist to draw from). Sermons stay as a secondary, tag-based
"related sermons" list — see build_occasion.sermon_recs, unchanged.

Notes are pulled straight from the reception store's wesley-notes rows — already
ingested + OSIS-keyed from ~/kjv-wesley (see reception-corpus's "WESLEY RCL
COMPANION" build; 96% RCL coverage, 17,920 verse-notes, 66 books). Uses the same
cross-chapter-aware span expansion as rcl.py's resolve_reading, so a reading like
Good Friday's John 18:1-19:42 pulls notes from every spanned chapter, not just
the first.
"""
from __future__ import annotations
import sqlite3, sys
from pathlib import Path

RECEPTION = Path.home() / "reception-corpus"
sys.path.insert(0, str(RECEPTION / "src"))
import rcl as rcl_mod  # noqa: E402  (chapter_query_spans)

DB = RECEPTION / "data" / "reception.sqlite"


def connect() -> sqlite3.Connection:
    return sqlite3.connect(DB)


def notes_for_refkey(refkey: str, con: sqlite3.Connection) -> list[dict]:
    """Wesley's notes overlapping a refKey (verse-ordered, deduped across the
    refKey's spanned chapters)."""
    seen = set()
    out = []
    for book, ch, vlo, vhi in rcl_mod.chapter_query_spans(refkey):
        rows = con.execute(
            "SELECT chapter, v_start, v_end, text FROM reception "
            "WHERE source='wesley-notes' AND book=? AND chapter=? "
            "AND v_start<=? AND v_end>=? ORDER BY v_start",
            (book, ch, vhi, vlo)).fetchall()
        for c, vs, ve, text in rows:
            key = (c, vs, ve)
            if key in seen:
                continue
            seen.add(key)
            out.append({"chapter": c, "v_start": vs, "v_end": ve, "text": text})
    out.sort(key=lambda n: (n["chapter"], n["v_start"]))
    return out


if __name__ == "__main__":
    rk = sys.argv[1] if len(sys.argv) > 1 else "Matt.22.1-Matt.22.14"
    con = connect()
    for n in notes_for_refkey(rk, con):
        vrange = f"{n['v_start']}" + (f"-{n['v_end']}" if n["v_end"] != n["v_start"] else "")
        print(f"  {n['chapter']}:{vrange}  {n['text'][:100]}")
