#!/usr/bin/env python3.11
"""Lectern — Call to Worship generator (proof-of-feel stage).

Given an RCL occasion id, pull that Sunday's readings from the SHARED spine in
~/reception-corpus (the data hub — do NOT fork the spine here) and assemble the
draft bundle: season + readings + the voice spec. This is the deterministic half
of the pipeline; the generative half (drafting the call in Wilson's voice) reads
this bundle plus corpus/calls-to-worship/voice.md.

Usage:
    python3.11 src/call_to_worship.py <occasion-id>
    python3.11 src/call_to_worship.py --list            # list occasion ids
    python3.11 src/call_to_worship.py --list Lent        # filter by season/name
"""
from __future__ import annotations
import json, sys
from pathlib import Path

RECEPTION = Path.home() / "reception-corpus"
SPINE = RECEPTION / "data" / "rcl.json"
LECTERN = Path(__file__).resolve().parent.parent
VOICE = LECTERN / "corpus" / "calls-to-worship" / "voice.md"


def load_spine() -> dict:
    if not SPINE.exists():
        sys.exit(f"RCL spine not found at {SPINE} — is ~/reception-corpus present?")
    return json.loads(SPINE.read_text(encoding="utf-8"))


def find(spine: dict, occ_id: str) -> dict | None:
    return next((o for o in spine["occasions"] if o["id"] == occ_id), None)


def bundle(occ: dict) -> dict:
    """The deterministic draft bundle: what the day actually appoints."""
    by_role: dict[str, list[dict]] = {}
    for r in occ["readings"]:
        by_role.setdefault(r["role"], []).append(
            {"refDisplay": r["refDisplay"], "alt": r.get("alt", False),
             "track": r.get("track")}
        )
    return {
        "id": occ["id"], "year": occ["year"],
        "season": occ.get("season"), "name": occ.get("name"),
        "readings": by_role,
    }


def main() -> None:
    args = sys.argv[1:]
    spine = load_spine()
    if not args or args[0] == "--list":
        needle = (args[1].lower() if len(args) > 1 else "")
        for o in spine["occasions"]:
            label = f"{o.get('season','')} · {o.get('name','')}"
            if needle in (o["id"] + label).lower():
                print(f"{o['id']:32}  {label}")
        return
    occ = find(spine, args[0])
    if not occ:
        sys.exit(f"No occasion '{args[0]}'. Try --list.")
    b = bundle(occ)
    print(json.dumps(b, indent=2, ensure_ascii=False))
    print(f"\n# Voice spec: {VOICE}")
    print("# Draft the call from the readings above, in that voice. "
          "Lean on the Psalm + Gospel; weave, don't quote.")


if __name__ == "__main__":
    main()
