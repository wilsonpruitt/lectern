#!/usr/bin/env python3.11
"""Tag every Wesley sermon against the FROZEN lexicon v1 (data/tags/lexicon.json) so
sermons connect to the lectionary by MEANING (shared faceted tags), the same way
hymns do — not by scripture coincidence alone.

Dual-tag (per reference_tagging-philosophy): each sermon keeps its own source-authentic
Wesley themes (already assigned in the corpus) for display, AND carries shared-lexicon
tags for the cross-item connection.

Three grounded signals (AI-drafted, for Wilson's curation — tags are acknowledged
interpretation, lower-stakes than factual attributions, but assigned FROM the frozen
list, never invented):
  theme   <- crosswalk from each sermon's existing Wesley corpus-themes -> v1 theme tags
  image/mood <- conservative keyword seeds over title + thesis (chunk 0)
  refKey  <- preaching text from the chunk-0 "Text:"/epigraph (+ CW title), via the
             reception-corpus citation parser; dropped if not cleanly parseable

Source: ~/wesley-corpus/chunked/cleaned_passages.jsonl (source_type='sermon').
Output: ~/lectern/data/tags/sermon_tags.json.
"""
from __future__ import annotations
import json, re, sys, collections
from pathlib import Path

LECTERN = Path(__file__).resolve().parent.parent
LEXICON = LECTERN / "data" / "tags" / "lexicon.json"
OUT = LECTERN / "data" / "tags" / "sermon_tags.json"
CORPUS = Path.home() / "wesley-corpus" / "chunked" / "cleaned_passages.jsonl"
sys.path.insert(0, str(Path.home() / "reception-corpus" / "src"))
import build_rcl, osis  # parse_citation, match_book, osis grammar

# ── Wesley corpus-theme -> frozen v1 lexicon tags (authored crosswalk) ──────────
# NB: v1 has no explicit sanctification/holiness/perfection THEME tag (Wesley's
# signature) -> mapped to the nearest (call-and-discipleship + faithfulness + love).
# Flagged as a candidate v1.1 addition; not forked here.
CROSSWALK = {
    "reign-of-god":          {"theme": ["kingdom-of-god"]},
    "repentance":            {"theme": ["repentance", "sin-and-fall"], "mood": ["penitence"]},
    "christology":           {"theme": ["atonement"]},
    "means-of-grace":        {"theme": ["prayer-and-worship", "word-of-god"]},
    "scriptural-authority":  {"theme": ["word-of-god"]},
    "universal-redemption":  {"theme": ["atonement", "grace"]},
    "catholic-spirit":       {"theme": ["church-and-unity"]},
    "sanctifying-grace":     {"theme": ["call-and-discipleship", "faithfulness"]},
    "free-will":             {"theme": ["grace"]},
    "pneumatology":          {"theme": ["holy-spirit"]},
    "trinity":               {"theme": ["trinity"]},
    "justifying-grace":      {"theme": ["grace", "mercy-and-forgiveness", "faith-and-trust"]},
    "works-mercy":           {"theme": ["justice", "love-of-neighbor"]},
    "social-holiness":       {"theme": ["church-and-unity", "love-of-neighbor", "justice"]},
    "works-piety":           {"theme": ["prayer-and-worship", "word-of-god"]},
    "assurance":             {"theme": ["faith-and-trust"], "mood": ["assurance"]},
    "primitive-christianity":{"theme": ["church-and-unity", "mission-and-witness"]},
    "experience":            {"theme": ["faith-and-trust"]},
    "christian-perfection":  {"theme": ["call-and-discipleship", "love-of-neighbor", "faithfulness"]},
    "prevenient-grace":      {"theme": ["grace"]},
    "communion":             {"function": ["table-communion"], "image": ["table-and-feast", "bread", "cup"]},
}

# ── conservative keyword seeds: lexicon tag -> trigger words (word-boundary) ─────
IMAGE_SEEDS = {
    "light": ["light", "lamp", "dawn", "shine", "shining"],
    "darkness-and-night": ["darkness", "asleep", "sleep ", "awake", "night"],
    "water": ["water", "fountain", "river", "thirst", "well of", "spring of"],
    "fire": ["fire", "flame", "burning", "kindle"],
    "wind-and-breath": ["wind", "breath"],
    "mountain": ["mountain", "sinai", "zion", "mount "],
    "wilderness": ["wilderness", "desert"],
    "road-and-journey": ["pilgrim", "the race", "run the race", "the way of", "journey"],
    "vineyard": ["vineyard", "the vine", "branches"],
    "harvest": ["harvest", "reap", "the field", "labourers", "laborers"],
    "seed-and-growth": ["the seed", "mustard", "the grain", "sown"],
    "shepherd": ["shepherd", "the flock", "the fold", "sheep"],
    "lamb": ["the lamb", "passover"],
    "table-and-feast": ["the feast", "banquet", "the supper", "the table", "wedding"],
    "bread": ["bread", "manna"],
    "cup": ["the cup"],
    "garment-and-robe": ["garment", "the robe", "clothed", "raiment"],
    "rock-and-refuge": ["the rock", "refuge", "fortress", "stronghold"],
    "gate-and-door": ["the gate", "the door", "narrow way"],
    "king-and-throne": ["throne", "the crown", "royal", "judgment seat", "assize"],
    "cross-and-tree": ["the cross", "crucified", "the tree"],
    "tomb-and-grave": ["the tomb", "the grave", "sepulchre", "buried"],
    "blood": ["the blood", "blood of"],
    "oil-and-anointing": ["anoint", "the oil"],
    "trumpet-and-voice": ["trumpet", "the last trump", "voice from heaven"],
    "yoke-and-burden": ["the yoke", "burden", "weary", "heavy laden", "the load"],
}
MOOD_SEEDS = {
    "penitence": ["repent", "contrite", "sorrow for sin", "mourn for"],
    "assurance": ["assurance", "witness of the spirit", "children of god", "full assurance"],
    "fear-and-trembling": ["wrath", "terror", "tremble", "dreadful", "the dread"],
    "prophetic-warning": ["beware", "woe ", "warning", "the wrath to come", "awake"],
    "comfort-and-consolation": ["comfort", "consolation", "rest to", "weary"],
    "joy": ["joy", "rejoice", "glad"],
    "longing-and-waiting": ["long for", "wait for", "yearn"],
    "wonder-and-awe": ["wonder", "marvel", "the awe"],
    "praise-and-exultation": ["praise", "magnify", "extol"],
    "trust": ["trust in", "rely on"],
    "tenderness": ["tender", "gentle"],
    "lament": ["lament", "weep"],
}

ROMAN = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100}
ABBREV = {"rom": "Romans", "cor": "Corinthians", "eph": "Ephesians", "phil": "Philippians",
          "col": "Colossians", "thess": "Thessalonians", "tim": "Timothy", "tit": "Titus",
          "heb": "Hebrews", "jas": "James", "pet": "Peter", "rev": "Revelation",
          "matt": "Matthew", "mk": "Mark", "lk": "Luke", "jn": "John", "ps": "Psalm",
          "psa": "Psalm", "prov": "Proverbs", "isa": "Isaiah", "jer": "Jeremiah",
          "gen": "Genesis", "exod": "Exodus", "deut": "Deuteronomy", "acts": "Acts",
          "gal": "Galatians", "mic": "Micah", "hos": "Hosea", "zech": "Zechariah"}


def roman_to_int(s):
    s = s.lower()
    if not s or any(ch not in ROMAN for ch in s):
        return None
    total, prev = 0, 0
    for ch in reversed(s):
        v = ROMAN[ch]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total or None


def _num(tok):
    tok = tok.strip().strip(".,")
    if tok.isdigit():
        return int(tok)
    return roman_to_int(tok)


def parse_preaching_ref(raw):
    """Best-effort: a raw epigraph reference string -> OSIS refKey, or None.
    Handles full or Wesley-abbreviated book names, arabic or roman chapter/verse,
    '.' or ':' separators. Returns None unless it parses cleanly (no guessing)."""
    raw = raw.strip().strip('".,;')
    m = re.match(r"^((?:[1-3]\s+)?[A-Za-z]+)\.?\s+([ivxlcIVXLC\d]+)[\s.:,]+([ivxlcIVXLC\d]+)"
                 r"(?:\s*-\s*([ivxlcIVXLC\d]+))?", raw)
    if not m:
        return None
    book_raw, c, v, v2 = m.groups()
    c, v = _num(c), _num(v)
    if not c or not v:
        return None
    bk = book_raw.strip()
    key = re.sub(r"^([1-3])\s+", "", bk).lower().rstrip(".")
    if key in ABBREV:                       # expand abbreviation, keep ordinal prefix
        pre = re.match(r"^([1-3])\s+", bk)
        full = ABBREV[key]
        bk = (pre.group(1) + " " if pre else "") + full
    cite = f"{bk} {c}:{v}" + (f"-{_num(v2)}" if v2 and _num(v2) else "")
    try:
        out = build_rcl.parse_citation(cite)
        p = osis.parse_refkey(out["refKey"])
        if p and p["book"] in osis.OSIS_NAME:
            return out["refKey"], out["refDisplay"]
    except Exception:
        return None
    return None


# a single scripture reference: optional ordinal, Book (abbrev/full), ch [:.] v [-v]
REF_RE = re.compile(r"((?:[1-3]\s+)?[A-Z][a-zA-Z]+)\.?\s+([ivxlcIVXLC]+|\d+)\s*[:.]\s*([ivxlcIVXLC]+|\d+)(?:\s*-\s*(\d+))?")


def extract_preaching(title, chunk0):
    # 1) CW (and some) titles embed the ref: "... : Proverbs 11:30"
    mt = re.search(r":\s*((?:[1-3]\s+)?[A-Z][a-zA-Z]+\s+\d+:\d+(?:-\d+)?)\s*$", title)
    if mt:
        r = parse_preaching_ref(mt.group(1))
        if r:
            return r
    # 2) the epigraph is the FIRST parseable scripture reference at the head of chunk 0
    #    (after the title/place/date line). Iterate matches; return the first that parses
    #    to a real book — "Sermon 1:", dates, etc. simply fail and are skipped.
    for m in REF_RE.finditer(chunk0[:500]):
        r = parse_preaching_ref(m.group(0))
        if r:
            return r
    return None


def seed_hits(text, seeds):
    t = text.lower()
    return [tag for tag, kws in seeds.items() if any(k in t for k in kws)]


def main():
    lex = json.loads(LEXICON.read_text())
    valid = {f: set(b["tags"]) for f, b in lex["facets"].items()}

    # gather sermons: union themes, chunk0 text, title, author
    serm = collections.defaultdict(lambda: {"themes": set(), "chunk0": "", "title": "", "author": ""})
    with CORPUS.open() as f:
        for line in f:
            r = json.loads(line)
            if r["source_type"] != "sermon":
                continue
            s = serm[r["source_id"]]
            s["title"] = r["source_title"]
            s["author"] = "Charles Wesley" if r["author"] == "charles-wesley" else "John Wesley"
            for t in (r.get("themes") or []):
                s["themes"].add(t)
            if r["chunk_index"] == 0:
                s["chunk0"] = r["text"]

    out = {}
    unknown_themes = set()
    with_text = 0
    for sid, s in sorted(serm.items()):
        facets = {"theme": set(), "image": set(), "mood": set(), "function": set()}
        for wt in s["themes"]:
            mapped = CROSSWALK.get(wt)
            if not mapped:
                unknown_themes.add(wt)
                continue
            for fac, tags in mapped.items():
                facets[fac].update(tags)
        scan = f"{s['title']} . {s['chunk0']}"
        facets["image"].update(seed_hits(scan, IMAGE_SEEDS))
        facets["mood"].update(seed_hits(scan, MOOD_SEEDS))
        facets["mood"].add("exhortation")              # sermons exhort, by genre
        # validate every emitted tag is in frozen v1
        for fac in facets:
            facets[fac] &= valid[fac]
        entry = {"title": s["title"], "author": s["author"],
                 "wesley_themes": sorted(s["themes"])}     # dual-tag: source-authentic side
        pt = extract_preaching(s["title"], s["chunk0"])
        if pt:
            entry["refKey"], entry["refDisplay"] = pt
            with_text += 1
        for fac in ("theme", "image", "mood", "function"):
            if facets[fac]:
                entry[fac] = sorted(facets[fac])
        out[sid] = entry

    doc = {
        "note": ("Wesley sermon tags against lexicon.json v1 (FROZEN). AI-DRAFTED for "
                 "curation. Dual-tag: `wesley_themes` = the sermon's own source-authentic "
                 "Wesley themes (from the corpus); theme/image/mood/function = shared-lexicon "
                 "tags for the sermon↔lectionary connection. `theme` is crosswalked from "
                 "wesley_themes; image/mood are conservative keyword-seed drafts (curate/deepen). "
                 "`refKey` = the sermon's preaching TEXT where cleanly parseable. NB: v1 lacks a "
                 "sanctification/holiness theme tag (Wesley's signature) — perfection/sanctifying "
                 "grace mapped to call-and-discipleship+faithfulness+love; candidate v1.1 add."),
        "source": "~/wesley-corpus (John & Charles Wesley sermons)",
        "lexicon_version": lex["version"],
        "sermons": out,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Tagged {len(out)} sermons -> {OUT}")
    print(f"  preaching text resolved: {with_text}/{len(out)}")
    print(f"  unmapped Wesley themes (should be none): {sorted(unknown_themes) or 'none'}")
    # facet coverage
    for fac in ("theme", "image", "mood", "function"):
        n = sum(1 for e in out.values() if e.get(fac))
        print(f"  sermons with ≥1 {fac}: {n}")


if __name__ == "__main__":
    main()
