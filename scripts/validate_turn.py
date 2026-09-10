#!/usr/bin/env python3.11
"""Validate corpus/turn/*.json against the Turn's load-bearing rule: never attribute
from recall, only from a retrieved text.

For every witness, on the passage its door is about (the card's Gospel refKey for
the shared doors, the track's firstReading refKey for firstReading doors):
  * the author must be attested in the reception store on that passage;
  * for Wesley's Notes, the Glossa ordinaria (Migne), and Catena's intertextual
    notes (tradition "intertext"), the witness `reading` must
    also be textually grounded: most of its content words must occur in that
    source's own rows for the passage. This catches a witness quoted from memory or
    slotted onto the wrong verse range. It does NOT judge whether the reading fits
    its door; that is the author's job and Wilson's curation.

And per card (Phase 4b requirement): the Gospel doors carry at least one Glossa
(Migne) and one Wesley witness wherever the store has rows for them, and every
track carries gravity + synthesis.

Exit 1 on any grounding failure. Missing-track and missing-requirement lines are
reported as WARN so a partially authored card can still be committed mid-pass.

Usage: python3.11 scripts/validate_turn.py [occasion-id ...]
"""
from __future__ import annotations
import json, re, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path.home() / "reception-corpus" / "src"))
import rcl as rcl_mod  # noqa: E402

DB = Path.home() / "reception-corpus" / "data" / "reception.sqlite"
TURN = ROOT / "corpus" / "turn"
MIGNE = "Glossa ordinaria (Migne)"
STOP = set("""the a an and of to in is he his that for was it they with not be shall you i we as
this which by or but are from on at so him them their her its our your my me what who whom when
there then than into upon unto have has had were been being do does did no nor all any one also
only even more most such these those thy thee thou hath doth saith""".split())
GROUND_MIN = 0.6


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z']+", s.lower()) if w not in STOP and len(w) > 2}


def rows(con, refkeys, where: str, args: tuple = ()) -> list[tuple]:
    """Rows on a passage; `refkeys` is one refKey or a list (every span of a split
    reading, from the card's firstReading.refKeys)."""
    out = []
    spans = [s for rk in ([refkeys] if isinstance(refkeys, str) else refkeys)
             for s in rcl_mod.chapter_query_spans(rk)]
    for book, ch, vlo, vhi in spans:
        out += con.execute(
            f"SELECT author, source, work, text FROM reception WHERE book=? AND chapter=? "
            f"AND v_start<=? AND v_end>=? AND {where}", (book, ch, vhi, vlo) + args).fetchall()
    return out


def check_witness(con, refkey: str, w: dict) -> str | None:
    if w.get("work") == MIGNE:
        src_rows = rows(con, refkey, "source='glossa-ordinaria'")
    elif w["author"] == "John Wesley":
        src_rows = rows(con, refkey, "source='wesley-notes'")
    elif w.get("tradition") == "intertext":
        src_rows = rows(con, refkey, "source='catena'")
    else:
        attested = rows(con, refkey, "author=?", (w["author"],))
        return None if attested else f"author {w['author']!r} not attested on {refkey}"
    if not src_rows:
        return f"no {w['author']} rows on {refkey}"
    pool = set().union(*(words(r[3] or "") for r in src_rows))
    ww = words(w["reading"])
    if not ww:
        return "empty reading"
    ratio = len(ww & pool) / len(ww)
    if ratio < GROUND_MIN:
        missing = sorted(ww - pool)[:8]
        return f"{w['author']} reading only {ratio:.0%} grounded on {refkey} (unmatched: {missing})"
    return None


def has_rows(con, refkey: str, source: str) -> bool:
    return bool(rows(con, refkey, "source=?", (source,)))


def validate(path: Path, con) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    c = json.loads(path.read_text(encoding="utf-8"))
    rk = c["refKey"]
    for i, d in enumerate(c["doors"]):
        for w in d["witnesses"]:
            e = check_witness(con, rk, w)
            if e:
                errs.append(f"gospel door {i+1}: {e}")
    gw = [w for d in c["doors"] for w in d["witnesses"]]
    if has_rows(con, rk, "glossa-ordinaria") and not any(w.get("work") == MIGNE for w in gw):
        warns.append("Gospel doors have no Glossa (Migne) witness, though the store has rows")
    if has_rows(con, rk, "wesley-notes") and not any(w["author"] == "John Wesley" for w in gw):
        warns.append("Gospel doors have no Wesley witness, though the store has rows")
    for tkey, t in c.get("tracks", {}).items():
        fr = t.get("firstReading") or {}
        for i, d in enumerate(fr.get("doors", [])):
            for w in d["witnesses"]:
                e = check_witness(con, fr.get("refKeys") or fr["refKey"], w)
                if e:
                    errs.append(f"{tkey} first-reading door {i+1}: {e}")
        if not t.get("gravity") or not t.get("synthesis"):
            warns.append(f"track {tkey} not yet authored (gravity/synthesis missing)")
    return errs, warns


def main():
    con = sqlite3.connect(DB)
    ids = sys.argv[1:]
    files = [TURN / f"{i}.json" for i in ids] if ids else sorted(TURN.glob("*.json"))
    bad = 0
    for f in files:
        errs, warns = validate(f, con)
        status = "FAIL" if errs else ("warn" if warns else "ok")
        print(f"{status:4}  {f.stem}")
        for e in errs:
            print(f"      ERROR {e}")
        for w in warns:
            print(f"      WARN  {w}")
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
