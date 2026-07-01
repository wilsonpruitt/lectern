#!/usr/bin/env python3.11
"""Sync the Greek study data baked in reception-corpus into Lectern's static API tree.

The word parsing + classical-lexicon data is produced by reception-corpus
(src/ingest_greek_nt.py + src/ingest_greek_lexicon.py). This step copies the exported JSON into
web/public/api/greek/ so it ships with the static export (CORS-open JSON, same pattern as the rest
of the Lectern API), and writes an index the /greek routes use for nav + generateStaticParams.

Layout produced under web/public/api/greek/:
  books/<Book>.json        per-book: verses → ordered parsed words (+ lexKey per word)
  short-glosses.json       {lexKey: concise classical gloss}   — inline, baked into the view
  lex/<enc(lexKey)>.json   per-lemma full Middle Liddell + LSJ entry — lazy-fetched on word click
  index.json               {books:[{code,name,chapters,verseCount}], refKeys:[...]}

Run from deploy.sh before `pnpm build`. Idempotent: wipes and re-copies web/public/api/greek.
"""
from __future__ import annotations
import json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path.home() / "reception-corpus" / "out"
DST = ROOT / "web" / "public" / "api" / "greek"


def main():
    nt, lex = SRC / "greek-nt", SRC / "greek-lexicon"
    if not nt.exists() or not lex.exists():
        raise SystemExit(f"missing reception-corpus exports at {SRC} — run the ingest scripts first")

    if DST.exists():
        shutil.rmtree(DST)
    (DST / "books").mkdir(parents=True)
    (DST / "lex").mkdir(parents=True)

    # per-book word files + build the route/nav index
    books, refkeys = [], []
    for f in sorted(nt.glob("*.json")):
        shutil.copy2(f, DST / "books" / f.name)
        d = json.loads(f.read_text(encoding="utf-8"))
        chapters: dict[int, int] = {}
        for v in d["verses"]:
            refkeys.append(v["refKey"])
            chapters[v["chapter"]] = max(chapters.get(v["chapter"], 0), v["verse"])
        books.append({"code": d["book"], "name": d["bookName"],
                      "verseCount": len(d["verses"]),
                      "chapters": {str(c): chapters[c] for c in sorted(chapters)}})

    # short glosses (inline) + per-lemma entries (lazy)
    shutil.copy2(lex / "short-glosses.json", DST / "short-glosses.json")
    entries = lex / "entries"
    n_lex = 0
    for f in entries.glob("*.json"):
        shutil.copy2(f, DST / "lex" / f.name)
        n_lex += 1

    (DST / "index.json").write_text(
        json.dumps({"books": books, "refKeys": refkeys}, ensure_ascii=False), encoding="utf-8")

    print(f"synced {len(books)} book(s), {len(refkeys)} verses, {n_lex} lexicon entries → {DST}")


if __name__ == "__main__":
    main()
