#!/usr/bin/env python3.11
"""Lectern — hymn recommendations keyed to the lectionary.

COPYRIGHT POSTURE: pointer-only. We store and emit hymn *numbers + hymnal*
(facts), never lyrics or music. The data is the hymnal's own back-of-book
Scripture Index (passage -> hymn number), which is reference data, not the
copyrighted expression.

Pipeline: hymnal Scripture Index (data/*_scripture_index.json) -> resolve each
citation to OSIS refKey via reception-corpus's parser (same keys as the RCL
spine, so the join is exact) -> for an RCL occasion, overlap the day's reading
refKeys with the index's refKeys -> surface hymns.

Hymnary.org enrichment (the "non-standard connections" layer) is a later pass;
this module is the canonical UMH/TFWS backbone.

Usage:
    python3.11 src/hymns.py proper-23-28-a
"""
from __future__ import annotations
import json, sys
from pathlib import Path

# reuse reception-corpus's battle-tested citation parser + OSIS resolver
RECEPTION_SRC = Path.home() / "reception-corpus" / "src"
sys.path.insert(0, str(RECEPTION_SRC))
import osis                       # noqa: E402
from build_rcl import parse_citation  # noqa: E402

LECTERN = Path(__file__).resolve().parent.parent
DATA = LECTERN / "data"
SPINE = Path.home() / "reception-corpus" / "data" / "rcl.json"


def _span(refkey: str):
    """(book, lo_ordinal, hi_ordinal) for overlap testing, or None.
    Ordinal = chapter*1000 + verse; whole-chapter end clamps to .999."""
    p = osis.parse_refkey(refkey)
    if not p or p["chapter"] == 0:          # book-level / unparseable -> skip
        return None
    lo = p["chapter"] * 1000 + p["v_start"]
    hi_v = p["v_end_true"] if p["v_end_true"] else 999
    hi = p["c_end"] * 1000 + hi_v
    return p["book"], lo, hi


def load_index(hymnal_file: str) -> list[dict]:
    """Resolve each Scripture-Index entry to refKey(s). Returns pointer rows:
    {book, lo, hi, hymnal, hymns, cite}."""
    blob = json.loads((DATA / hymnal_file).read_text(encoding="utf-8"))
    rows = []
    for e in blob["entries"]:
        try:
            parsed = parse_citation(e["cite"])
        except Exception:
            continue
        for rk in (parsed.get("refKeys") or [parsed["refKey"]]):
            s = _span(rk)
            if not s:
                continue
            book, lo, hi = s
            rows.append({"book": book, "lo": lo, "hi": hi,
                         "hymnal": blob["hymnal"], "hymns": e["hymns"],
                         "cite": e["cite"]})
    return rows


def hymns_for_reading(refkey: str, index_rows: list[dict]) -> list[dict]:
    s = _span(refkey)
    if not s:
        return []
    book, a_lo, a_hi = s
    return [r for r in index_rows
            if r["book"] == book and a_lo <= r["hi"] and r["lo"] <= a_hi]


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("usage: hymns.py <occasion-id>")
    occ_id = sys.argv[1]
    spine = json.loads(SPINE.read_text(encoding="utf-8"))
    occ = next((o for o in spine["occasions"] if o["id"] == occ_id), None)
    if not occ:
        sys.exit(f"no occasion {occ_id}")
    index_rows = load_index("umh_scripture_index.json")

    print(f"# {occ.get('season','')} · {occ.get('name','')} ({occ['year']})")
    print(f"# UMH hymn recs from the Scripture Index (pointer-only)\n")
    any_hit = False
    for r in occ["readings"]:
        hits = []
        for rk in (r.get("refKeys") or [r["refKey"]]):
            hits += hymns_for_reading(rk, index_rows)
        tag = f"[{r['role']}" + (f"/{r['track']}" if r.get('track') else "") + "]"
        if hits:
            any_hit = True
            nums = sorted({h for hit in hits for h in hit["hymns"]})
            print(f"{tag} {r['refDisplay']}")
            for hit in hits:
                print(f"    via {hit['cite']}: UMH {', '.join(map(str, hit['hymns']))}")
            print(f"    -> UMH {', '.join(map(str, nums))}\n")
        else:
            print(f"{tag} {r['refDisplay']} — no Scripture-Index hit "
                  f"(candidate for hymnary enrichment)\n")
    if not any_hit:
        print("(No print-index hits — exactly the case hymnary enrichment fills.)")


if __name__ == "__main__":
    main()
