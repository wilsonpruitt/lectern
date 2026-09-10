#!/usr/bin/env python3.11
"""Lectern — dump the retrieved witnesses a Turn card may cite, for one occasion.

The Turn's load-bearing rule: never attribute from recall, only from a retrieved
text. This prints the actual reception-store rows an author works from:

  * the Gospel pericope (the shared doors): Glossa ordinaria (Migne) + Wesley's
    Notes in full, and a count of every other tradition on file;
  * each track's first reading and psalm (the per-track gravity/synthesis and the
    optional firstReading doors): Glossa + Wesley in full, others counted.

Usage:
    python3.11 src/turn_pull.py proper-13-18-a            # to stdout
    python3.11 src/turn_pull.py proper-13-18-a --out DIR  # writes DIR/<id>.txt

Re-created 2026-09-10 for Phase 4b (the old scratchpad copy was gone); it lives in
src/ now so it doesn't vanish again.
"""
from __future__ import annotations
import argparse, json, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wesley_notes as wn   # noqa: E402
import glossa as gl         # noqa: E402

LECTERN = HERE.parent
BUILD = LECTERN / "data" / "build"
DB = Path.home() / "reception-corpus" / "data" / "reception.sqlite"
sys.path.insert(0, str(Path.home() / "reception-corpus" / "src"))
import rcl as rcl_mod  # noqa: E402


def other_counts(refkey: str, con) -> dict[str, int]:
    out: dict[str, int] = {}
    for book, ch, vlo, vhi in rcl_mod.chapter_query_spans(refkey):
        for (src, n) in con.execute(
                "SELECT source, COUNT(*) FROM reception WHERE book=? AND chapter=? "
                "AND v_start<=? AND v_end>=? AND source NOT IN ('glossa-ordinaria','wesley-notes') "
                "GROUP BY source", (book, ch, vhi, vlo)):
            out[src] = out.get(src, 0) + n
    return out


SPINE = Path.home() / "reception-corpus" / "data" / "rcl.json"
_spine = None


def all_spans(occ_id: str, refkey: str) -> list[str]:
    """Every span of a reading. The build only carries the primary refKey, but the
    RCL spine keeps `refKeys` for split readings (e.g. Gen 24:34-38, 42-49, 58-67)."""
    global _spine
    if _spine is None:
        _spine = {o["id"]: o for o in json.loads(SPINE.read_text(encoding="utf-8"))["occasions"]}
    for r in _spine.get(occ_id, {}).get("readings", []):
        if r.get("refKey") == refkey and r.get("refKeys"):
            return r["refKeys"]
    return [refkey]


def _union(fn, refkeys, con):
    seen, out = set(), []
    for rk in refkeys:
        for e in fn(rk, con):
            k = (e["chapter"], e["v_start"], e["v_end"])
            if k not in seen:
                seen.add(k)
                out.append(e)
    return sorted(out, key=lambda e: (e["chapter"], e["v_start"]))


def block(label: str, ref: str, refkeys: list[str], con) -> list[str]:
    lines = [f"\n######## {label}: {ref}  {refkeys}"]
    g = _union(gl.glosses_for_refkey, refkeys, con)
    lines.append(f"-- GLOSSA ORDINARIA (Migne) — {len(g)} entries")
    for e in g:
        v = f"{e['chapter']}:{e['v_start']}" + (f"-{e['v_end']}" if e['v_end'] != e['v_start'] else "")
        lines.append(f"[G {v}] {e['text']}")
    w = _union(wn.notes_for_refkey, refkeys, con)
    lines.append(f"-- WESLEY'S NOTES — {len(w)} notes")
    for n in w:
        v = f"{n['chapter']}:{n['v_start']}" + (f"-{n['v_end']}" if n['v_end'] != n['v_start'] else "")
        lines.append(f"[W {v}] {n['text']}")
    oc: dict[str, int] = {}
    for rk in refkeys:
        for k, v in other_counts(rk, con).items():
            oc[k] = oc.get(k, 0) + v
    lines.append("-- other sources on file: " + (", ".join(f"{k}={v}" for k, v in sorted(oc.items())) or "none"))
    return lines


def pull(occ_id: str) -> str:
    doc = json.loads((BUILD / f"{occ_id}.json").read_text(encoding="utf-8"))
    card = json.loads((LECTERN / "corpus" / "turn" / f"{occ_id}.json").read_text(encoding="utf-8"))
    con = sqlite3.connect(DB)
    out = [f"=== {occ_id} — {doc['occasion'].get('name')} ==="]
    out += block("GOSPEL (shared doors)", card["pericope"], [card["refKey"]], con)
    for tkey, t in doc["tracks"].items():
        for r in t["readings"]:
            if r["role"] in ("first", "psalm"):
                out += block(f"{tkey.upper()} {r['role']}", r["ref"], all_spans(occ_id, r["refKey"]), con)
    # the shared second reading, once, for the synthesis
    first_track = next(iter(doc["tracks"].values()))
    for r in first_track["readings"]:
        if r["role"] == "second":
            out.append(f"\n######## SECOND (shared): {r['ref']}  [{r['refKey']}] — "
                       f"{len(wn.notes_for_refkey(r['refKey'], con))} Wesley notes, "
                       f"{len(gl.glosses_for_refkey(r['refKey'], con))} Glossa entries (not dumped)")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("occasion")
    ap.add_argument("--out")
    a = ap.parse_args()
    text = pull(a.occasion)
    if a.out:
        Path(a.out).mkdir(parents=True, exist_ok=True)
        p = Path(a.out) / f"{a.occasion}.txt"
        p.write_text(text, encoding="utf-8")
        print(f"wrote {p} ({len(text)} chars)")
    else:
        sys.stdout.write(text)
