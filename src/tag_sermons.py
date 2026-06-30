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
# Tight, mostly-1:1 mapping so theme tags stay DISTINCTIVE (broad fan-out makes every
# sermon look alike — the "shared context swamping distinctive" failure). Only a sermon's
# DOMINANT Wesley themes (top few by chunk-frequency) are crosswalked, not every incidental
# mention. Discrimination then comes from the concrete/affective axes (image, mood).
CROSSWALK = {
    "reign-of-god":          {"theme": ["kingdom-of-god"]},
    "repentance":            {"theme": ["repentance"], "mood": ["penitence"]},
    "christology":           {"theme": ["atonement"]},
    "means-of-grace":        {"theme": ["prayer-and-worship"]},
    "scriptural-authority":  {"theme": ["word-of-god"]},
    "universal-redemption":  {"theme": ["atonement"]},
    "catholic-spirit":       {"theme": ["church-and-unity"]},
    "sanctifying-grace":     {"theme": ["call-and-discipleship"]},
    "free-will":             {"theme": ["grace"]},
    "pneumatology":          {"theme": ["holy-spirit"]},
    "trinity":               {"theme": ["trinity"]},
    "justifying-grace":      {"theme": ["grace"]},
    "works-mercy":           {"theme": ["love-of-neighbor"]},
    "social-holiness":       {"theme": ["love-of-neighbor"]},
    "works-piety":           {"theme": ["prayer-and-worship"]},
    "assurance":             {"mood": ["assurance"]},
    "primitive-christianity":{"theme": ["church-and-unity"]},
    "experience":            {"mood": ["assurance"]},
    "christian-perfection":  {"theme": ["call-and-discipleship"]},
    "prevenient-grace":      {"theme": ["grace"]},
    "communion":             {"function": ["table-communion"], "image": ["table-and-feast"]},
}
TOP_THEMES = 4          # keep only each sermon's most dominant Wesley themes
MIN_THEME_CHUNKS = 2    # ignore a theme mentioned in just one chunk

# ── conservative keyword seeds: lexicon tag -> trigger words (word-boundary) ─────
# High-precision only: a sermon's CONTROLLING image, scanned over title + thesis (chunk 0).
# Image is the heaviest connection axis (weight 1.5), so a false image tag is the most
# damaging — generic words (light, the table, king) are deliberately omitted. Capped per
# sermon below. Image is the thinnest, most curate-me facet by design.
IMAGE_SEEDS = {
    "wilderness": ["wilderness", "the desert"],
    "wind-and-breath": ["the rushing wind", "breath of life"],
    "fire": ["tongues of fire", "refining fire", "the flame of"],
    "water": ["living water", "the fountain", "wells of"],
    "vineyard": ["the vineyard", "vine and branches"],
    "harvest": ["the harvest", "reap", "the labourers", "the laborers"],
    "seed-and-growth": ["the mustard", "the sown seed", "grain of"],
    "shepherd": ["the good shepherd", "the flock", "the fold"],
    "lamb": ["the lamb of god", "the paschal lamb", "passover"],
    "table-and-feast": ["the marriage feast", "the wedding", "the great supper", "the banquet"],
    "bread": ["the bread of life", "manna"],
    "garment-and-robe": ["the wedding garment", "wedding-garment", "the robe of"],
    "rock-and-refuge": ["the rock of", "our refuge", "strong fortress"],
    "gate-and-door": ["the narrow gate", "the strait gate", "the narrow way"],
    "king-and-throne": ["judgment-seat", "judgment seat", "the great white throne", "the throne of"],
    "cross-and-tree": ["the cross of christ", "crucified with"],
    "tomb-and-grave": ["the sealed tomb", "the sepulchre"],
    "blood": ["the blood of christ", "blood of sprinkling"],
    "trumpet-and-voice": ["the last trump", "the trumpet shall", "voice of the archangel"],
    "yoke-and-burden": ["heavy laden", "the yoke of", "rest for your souls"],
}
MAX_IMAGE = 3
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

    # gather sermons: per-theme CHUNK COUNTS (for dominance), chunk0 text, title, author
    serm = collections.defaultdict(
        lambda: {"tc": collections.Counter(), "chunk0": "", "title": "", "author": ""})
    with CORPUS.open() as f:
        for line in f:
            r = json.loads(line)
            if r["source_type"] != "sermon":
                continue
            s = serm[r["source_id"]]
            s["title"] = r["source_title"]
            s["author"] = "Charles Wesley" if r["author"] == "charles-wesley" else "John Wesley"
            for t in (r.get("themes") or []):
                s["tc"][t] += 1
            if r["chunk_index"] == 0:
                s["chunk0"] = r["text"]

    out = {}
    unknown_themes = set()
    with_text = 0
    for sid, s in sorted(serm.items()):
        facets = {"theme": set(), "image": set(), "mood": set(), "function": set()}
        # a sermon's DOMINANT themes only: chunk-count >= MIN, top TOP_THEMES
        dominant = [t for t, c in s["tc"].most_common() if c >= MIN_THEME_CHUNKS][:TOP_THEMES]
        all_themes = sorted(s["tc"])
        for wt in dominant:
            mapped = CROSSWALK.get(wt)
            if not mapped:
                unknown_themes.add(wt)
                continue
            for fac, tags in mapped.items():
                facets[fac].update(tags)
        scan = f"{s['title']} . {s['chunk0']}"
        img = seed_hits(scan, IMAGE_SEEDS)[:MAX_IMAGE]
        facets["image"].update(img)
        facets["mood"].update(seed_hits(scan, MOOD_SEEDS))
        # NB: deliberately do NOT add a blanket "exhortation" mood — it's true of every
        # sermon by genre, so it carries zero discrimination and only swamps the
        # connection score + the "via" line (reference_tagging-philosophy: shared context
        # swamping distinctive context).
        # validate every emitted tag is in frozen v1
        for fac in facets:
            facets[fac] &= valid[fac]
        entry = {"title": s["title"], "author": s["author"],
                 "wesley_themes": all_themes,               # dual-tag: full source-authentic side
                 "dominant_themes": dominant}               # what drove the lexicon theme tags
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
