#!/usr/bin/env python3.11
"""Lectern — the Glossa ordinaria on the day's readings.

Mirrors wesley_notes.py exactly, against source='glossa-ordinaria' instead of
'wesley-notes'. Rows are pulled from the reception store's Glossa ingest (see
reception-corpus/src/ingest_glossa.py; 13,686 rows, 55 of the 56 Migne books,
Baruch has none by Migne's own note). Uses the same cross-chapter-aware span
expansion as rcl.py's resolve_reading, so a multi-chapter reading pulls glosses
from every spanned chapter, not just the first.

Coverage is NOT whole-Bible (58 books total minus Baruch's empty one = 55; the
Migne recension itself omits Lamentations, Ezekiel, Daniel, the twelve minor
prophets, and Maccabees) and it is Migne's abridged 19th-c. recension --
marginal gloss only, no interlinear layer, misattributed on its title page to
Walafrid Strabo. web/components/Workbench.tsx's Glossa tab states this; keep
that honesty line if this module's callers change.
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


def glosses_for_refkey(refkey: str, con: sqlite3.Connection) -> list[dict]:
    """Glossa ordinaria entries overlapping a refKey (verse-ordered, deduped
    across the refKey's spanned chapters)."""
    seen = set()
    out = []
    for book, ch, vlo, vhi in rcl_mod.chapter_query_spans(refkey):
        rows = con.execute(
            "SELECT chapter, v_start, v_end, text, anchor FROM reception "
            "WHERE source='glossa-ordinaria' AND book=? AND chapter=? "
            "AND v_start<=? AND v_end>=? ORDER BY v_start",
            (book, ch, vhi, vlo)).fetchall()
        for c, vs, ve, text, anchor in rows:
            key = (c, vs, ve)
            if key in seen:
                continue
            seen.add(key)
            out.append({"chapter": c, "v_start": vs, "v_end": ve, "text": text,
                        "anchor": anchor})
    out.sort(key=lambda n: (n["chapter"], n["v_start"]))
    return out


def book_has_glossa(book: str, con: sqlite3.Connection) -> bool:
    """Whether Migne's recension covers this OSIS book at all -- lets the tab
    distinguish 'no comment on this passage' from 'this book isn't in Migne'."""
    row = con.execute("SELECT 1 FROM reception WHERE source='glossa-ordinaria' "
                       "AND book=? LIMIT 1", (book,)).fetchone()
    return row is not None


if __name__ == "__main__":
    rk = sys.argv[1] if len(sys.argv) > 1 else "Matt.22.1-Matt.22.14"
    con = connect()
    for n in glosses_for_refkey(rk, con):
        vrange = f"{n['v_start']}" + (f"-{n['v_end']}" if n["v_end"] != n["v_start"] else "")
        print(f"  {n['chapter']}:{vrange}  {n['text'][:100]}")
