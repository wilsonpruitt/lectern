#!/usr/bin/env python3.11
"""Validate tag files against the frozen lexicon, and emit the untagged-reading
worklist. The lexicon is the leash: every tag on a reading or hymn MUST exist in
lexicon.json, else it's flagged (drift). Run after any tagging pass.

Usage:
    python3.11 src/validate_tags.py            # validate + coverage report
    python3.11 src/validate_tags.py --worklist # dump untagged unique readings JSON
"""
from __future__ import annotations
import json, sys
from pathlib import Path

LECTERN = Path(__file__).resolve().parent.parent
TAGS = LECTERN / "data" / "tags"
SPINE = Path.home() / "reception-corpus" / "data" / "rcl.json"
FACETS = ("theme", "image", "mood", "function")


def lexicon_sets():
    lex = json.loads((TAGS / "lexicon.json").read_text())
    return {f: set(lex["facets"][f]["tags"]) for f in FACETS}, lex.get("version")


def check(label, items, valid):
    bad = []
    for key, tagdict in items:
        for f in FACETS:
            for t in tagdict.get(f, []):
                if t not in valid[f]:
                    bad.append((label, key, f, t))
    return bad


def unique_readings():
    spine = json.loads(SPINE.read_text())
    seen, rows = set(), []
    for o in spine["occasions"]:
        for r in o["readings"]:
            if r.get("alt"):
                continue
            rk = r["refKey"]
            if rk in seen:
                continue
            seen.add(rk)
            rows.append({"refKey": rk, "refDisplay": r["refDisplay"],
                         "role": r["role"], "season": o.get("season"),
                         "year": o["year"], "occasion": o.get("name")})
    return rows


def main():
    valid, version = lexicon_sets()
    rcl = json.loads((TAGS / "rcl_tags.json").read_text())["readings"]
    hymns = json.loads((TAGS / "hymn_tags.json").read_text())["hymns"]

    if "--worklist" in sys.argv:
        done = set(rcl)
        todo = [r for r in unique_readings() if r["refKey"] not in done]
        print(json.dumps(todo, ensure_ascii=False, indent=2))
        return

    sermon_path = TAGS / "sermon_tags.json"
    sermons = json.loads(sermon_path.read_text())["sermons"] if sermon_path.exists() else {}

    bad = check("rcl", rcl.items(), valid)
    bad += check("hymn", [(f"{h['hymnal']} {h['number']}", h) for h in hymns], valid)
    bad += check("sermon", sermons.items(), valid)

    allrk = {r["refKey"] for r in unique_readings()}
    tagged = set(rcl) & allrk
    print(f"lexicon {version}: "
          f"{sum(len(v) for v in valid.values())} tags across {len(FACETS)} facets")
    print(f"RCL coverage: {len(tagged)}/{len(allrk)} unique readings tagged "
          f"({100*len(tagged)//max(len(allrk),1)}%)")
    print(f"hymns tagged: {len(hymns)}  ·  sermons tagged: {len(sermons)}")
    if bad:
        print(f"\n!! {len(bad)} UNKNOWN tags (not in lexicon):")
        for label, key, f, t in bad[:50]:
            print(f"   [{label}] {key}  {f}:{t}")
    else:
        print("OK — every tag exists in the frozen lexicon.")
    # readings tagged but not in spine (stale)
    stale = set(rcl) - allrk
    if stale:
        print(f"\nnote: {len(stale)} tagged refKeys not in current spine: "
              f"{sorted(stale)[:10]}")


if __name__ == "__main__":
    main()
