#!/usr/bin/env python3.11
"""Lectern — the Turn's reception backend helpers.

The Turn's witnesses are a projection of the reception store
(~/reception-corpus/data/reception.sqlite), whose rows already carry
source / author / tradition / work / mode. That makes the Turn EASY TO SUPPLEMENT:
to add Barth, Luther, the Philokalia, etc., ingest them into the reception store
with their tradition + mode, and they become available to slot into a door — no
schema change here.

Witness schema (corpus/turn/<id>.json doors[].witnesses[]):
    { author, tradition, work, mode, reading, cite? }
  - tradition: canonical key from the store (latin-patristic, greek-patristic,
    medieval, pseudonymous, wesleyan, reformed, reformation, eastern, modern, …);
    TRADITION_LABEL maps it to a display name.
  - mode: "text"    -> public-domain; `reading` is a grounded summary/short quote.
          "pointer" -> in-copyright (e.g. Barth); `reading` is OUR one-line gloss,
                       `cite` points to WHERE it is treated; the source's prose is
                       NEVER stored or shown. (Same posture as hymns/Barth.)

`available(refKey)` lists every reception row that resolves to a pericope, grouped
by tradition — run it when a new source lands to see what's ready to slot in.
"""
from __future__ import annotations
import sqlite3, re, sys
from pathlib import Path

DB = Path.home() / "reception-corpus" / "data" / "reception.sqlite"

# canonical tradition key -> display label (extend as new traditions are ingested)
TRADITION_LABEL = {
    "latin-patristic": "Latin Fathers",
    "greek-patristic": "Greek Fathers",
    "pseudonymous": "Greek Fathers (attrib.)",
    "medieval": "Medieval",
    "conciliar": "Conciliar",
    "jewish": "Jewish",
    "wesleyan": "Wesleyan",
    "Methodist": "Wesleyan",
    "reformed": "Reformed",
    "reformation": "Reformation",
    "puritan": "Puritan",
    "protestant-19c": "19th-c. Protestant",
    "eastern": "Eastern / Philokalic",
    "modern": "Modern",
    "intertext": "Scripture echo",
}

# author -> tradition for the public-domain Fathers/voices we author from by hand
# (the store records this per row; this mirror keeps card-authoring consistent).
AUTHOR_TRADITION = {
    "Augustine": "latin-patristic", "Gregory the Great": "latin-patristic",
    "Jerome": "latin-patristic", "Hilary of Poitiers": "latin-patristic",
    "Ambrose": "latin-patristic", "Leo the Great": "latin-patristic",
    "Origen": "greek-patristic", "John Chrysostom": "greek-patristic",
    "Cyril of Alexandria": "greek-patristic", "Basil": "greek-patristic",
    "Gregory Nazianzen": "greek-patristic", "Theophylact": "greek-patristic",
    "Pseudo-Chrysostom": "pseudonymous",
    "Remigius of Auxerre": "medieval", "Rabanus Maurus": "medieval",
    "Glossa Ordinaria": "medieval", "Bede": "medieval", "Anselm": "medieval",
    "John Wesley": "wesleyan", "Charles Wesley": "wesleyan",
    "John Calvin": "reformed", "Martin Luther": "reformation",
}


def tradition_for(author: str) -> str:
    return AUTHOR_TRADITION.get(author, "unknown")


def _con():
    return sqlite3.connect(DB)


def available(refkey: str) -> dict:
    """Every reception row resolving to a pericope, grouped by tradition. Use this
    to see what is ready to slot into a door — including newly-ingested sources."""
    m = re.match(r"([0-9A-Za-z]+)\.(\d+)\.(\d+)(?:-[0-9A-Za-z]+\.(\d+)\.(\d+))?", refkey)
    bk, c1, v1 = m.group(1), int(m.group(2)), int(m.group(3))
    v2 = int(m.group(5)) if m.group(5) else v1
    rows = _con().execute(
        "select author, tradition, source, mode, work, substr(text,1,160) "
        "from reception where book=? and chapter=? and v_start<=? and v_end>=? "
        "order by tradition, v_start, id", (bk, c1, v2, v1)).fetchall()
    out: dict[str, list] = {}
    for author, tr, source, mode, work, snippet in rows:
        out.setdefault(tr or source, []).append(
            {"author": author, "source": source, "mode": mode,
             "work": work, "snippet": (snippet or "").strip()})
    return out


if __name__ == "__main__":
    rk = sys.argv[1] if len(sys.argv) > 1 else "Matt.22.1-Matt.22.14"
    for tr, items in available(rk).items():
        print(f"\n== {TRADITION_LABEL.get(tr, tr)} ({tr}) — {len(items)} ==")
        for it in items[:6]:
            print(f"  [{it['author']}/{it['mode']}] {it['snippet'][:90]}")
