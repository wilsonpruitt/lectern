"""Link a reading to its passage in the Wroot Press Bible (bible.wrootpress.com) -- only when
every chapter the reading touches is PUBLISHED there, so Lectern never shows a dead link while
the WPB grows chapter by chapter.

Source of truth: WPB's verse register, /api/verses/{Book}.json, which lists per edition the
chapters that are published and maps English verse numbers to the edition's own (Psalms by the
Masoretic number: English Ps 51:1 is MT 51:3). The RCL spine is in English numbers, so every
span is mapped before the address is built.

`python3.11 src/wpb_links.py --refresh` re-fetches the live register into data/wpb-register.json
(deploy.sh runs it; a failed fetch keeps the cached copy). The live site, not ~/wpb/site/dist,
is the source: dist may hold chapters that are built but not yet released.

Scope: Masoretic (Hebrew Bible) and NT books. LXX-only books (Wisdom, Sirach, Baruch) are left
unlinked: none is published yet, and Swete's Sirach numbering departs from English Bibles.
"""
from __future__ import annotations
import json, sys, urllib.request
from pathlib import Path

BASE = "https://bible.wrootpress.com"
REGISTER = Path(__file__).resolve().parent.parent / "data" / "wpb-register.json"

_reg: dict | None = None


def _load() -> dict:
    global _reg
    if _reg is None:
        _reg = json.loads(REGISTER.read_text()) if REGISTER.exists() else {}
    return _reg


def refresh() -> None:
    """Fetch the live register for every book in WPB's index; keep the cache on any failure."""
    def get(path: str):
        with urllib.request.urlopen(f"{BASE}{path}", timeout=30) as r:
            return json.load(r)
    try:
        books = get("/api/verses/index.json")["books"]
        out = {}
        for code in books:
            d = get(f"/api/verses/{code}.json")
            # keep only what the linker needs: published chapters, verse lists, English maps
            out[code] = {
                "slug": d["slug"],
                "texts": {ed: {"published": t.get("published", []), "chapters": t.get("chapters", {})}
                          for ed, t in d["texts"].items() if ed in ("mt", "nt")},
                "en_mt": d.get("en_mt", {}),
                "en_nt": d.get("en_nt", {}),
            }
    except Exception as e:  # network down, schema change: build with the cached copy
        print(f"wpb_links: refresh failed ({e}); using cached {REGISTER.name}", file=sys.stderr)
        return
    REGISTER.write_text(json.dumps(out, separators=(",", ":"), sort_keys=True))
    pub = sum(len(t["published"]) for b in out.values() for t in b["texts"].values())
    print(f"wpb_links: {len(out)} books, {pub} published chapters -> {REGISTER.name}")


def _span(key: str):
    """'Gen.24.34-Gen.24.38' | 'Ps.65' | 'Luke.17.11' -> (book, c1, v1|None, c2, v2|None)."""
    a, _, b = key.partition("-")
    pa = a.split(".")
    pb = (b or a).split(".")
    if pb[0] != pa[0]:
        return None  # a span across books: no single page to send it to
    v1 = int(pa[2]) if len(pa) > 2 else None
    v2 = int(pb[2]) if len(pb) > 2 else None
    return pa[0], int(pa[1]), v1, int(pb[1]), v2


def wpb_href(refkeys: list[str]) -> str | None:
    """Absolute WPB URL for the reading, or None if any part of it isn't published."""
    reg = _load()
    spans = [_span(k) for k in refkeys]
    if not spans or None in spans or len({s[0] for s in spans}) != 1:
        return None
    book = reg.get(spans[0][0])
    if not book:
        return None
    ed = "nt" if "nt" in book["texts"] else "mt" if "mt" in book["texts"] else None
    if not ed:
        return None
    text = book["texts"][ed]
    en_map = book["en_nt"] if ed == "nt" else book["en_mt"]
    published = set(text["published"])

    def to_ed(c: int, v: int, last: bool) -> tuple[int, int] | None:
        """English c:v -> the edition's own c:v (an English verse may be split over two)."""
        keys = en_map.get(f"{c}.{v}") or [f"{c}.{v}"]
        ck, vk = keys[-1 if last else 0].split(".")
        if vk not in text["chapters"].get(ck, []):
            return None
        return int(ck), int(vk)

    mapped = []  # [(c1, v1, c2, v2)] in edition numbers; v None = whole chapter
    for _, c1, v1, c2, v2 in spans:
        if v1 is None:  # whole chapter(s): follow verse 1 in case the chapter number moves
            s = to_ed(c1, 1, False)
            e = to_ed(c2, 1, False)
            if not s or not e:
                return None
            mapped.append((s[0], None, e[0], None))
            continue
        s, e = to_ed(c1, v1, False), to_ed(c2, v2 if v2 is not None else v1, True)
        if not s or not e:
            return None
        mapped.append((s[0], s[1], e[0], e[1]))

    # RCL order puts an optional '(1-8)' after the core span; the address wants reading order,
    # with overlapping or adjacent spans ('1-9a, 9b-12') run together
    mapped.sort(key=lambda m: (m[0], m[1] or 0))
    merged = [mapped[0]]
    for m in mapped[1:]:
        p = merged[-1]
        if None not in (m[1], p[3]) and m[0] == p[2] and m[1] <= p[3] + 1:
            merged[-1] = (p[0], p[1], max((p[2], p[3]), (m[2], m[3]))[0], max((p[2], p[3]), (m[2], m[3]))[1])
        else:
            merged.append(m)
    mapped = merged

    first_c = mapped[0][0]
    last_c = max(m[2] for m in mapped)
    if any(str(c) not in published for c in range(first_c, last_c + 1)):
        return None

    path = f"{BASE}/{ed}/{book['slug']}/{first_c}"
    if all(m[1] is None for m in mapped):
        return path if first_c == last_c else f"{path}/1-{last_c}:{len(text['chapters'][str(last_c)])}"
    if any(m[1] is None for m in mapped):
        return path  # mixed whole-chapter + verse spans: the chapter page is the honest landing
    if all(m[0] == first_c and m[2] == first_c for m in mapped):
        segs = [f"{m[1]}" if m[1] == m[3] else f"{m[1]}-{m[3]}" for m in mapped]
        return f"{path}/{','.join(segs)}"
    # spans in more than one chapter: the whole run, start to end ('12-4:2')
    end = mapped[-1]
    return f"{path}/{mapped[0][1]}-{end[2]}:{end[3]}"


if __name__ == "__main__":
    if "--refresh" in sys.argv:
        refresh()
    for k in sys.argv[1:]:
        if k != "--refresh":
            print(k, "->", wpb_href(k.split(",")))
