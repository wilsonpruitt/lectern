#!/usr/bin/env python3.11
"""Lectern — the connective layer: for each reading, the TOOLS FOR INTERPRETATION
in the Wroot Press / Wroot Labs family that resolve to it. Lectern is not a Bible;
it points to how a text has been read (Catena), where it happened (Topographia),
when (Annales), and what it means for belief (Doctrine).

Source-first: coverage + routes were read from each resource's own repo (slugs,
manifests, edition ranges, document files), so we link only where the resource
actually resolves — no dead links. Greek/Hebrew tools are a future addition; we do
NOT host the bare text here on purpose.

Two kinds of connection:
  - reading_links(refKey)  — scripture-keyed: Catena / Topographia / Annales.
  - doctrine_links(themes) — theme-keyed: the day's faceted themes -> creed /
    confession documents (the theological-application surface).
"""
from __future__ import annotations
import sys
from pathlib import Path

RECEPTION_SRC = Path.home() / "reception-corpus" / "src"
sys.path.insert(0, str(RECEPTION_SRC))
import osis  # noqa: E402  (parse_refkey -> {book, chapter, ...})

CATENA = "https://catena.wrootpress.com"
TOPO = "https://topographia.wrootpress.com"
ANNALES = "https://annales.wrootpress.com"
DOCTRINE = "https://doctrine.wrootpress.com"

# --- Catena: NT books are full readers at /<slug>; everything else -> /fontium ---
CATENA_NT_SLUG = {
    "Matt": "matthew", "Mark": "mark", "Luke": "luke", "John": "john",
    "Acts": "acts", "Rom": "romans", "1Cor": "1-corinthians",
    "2Cor": "2-corinthians", "Gal": "galatians", "Eph": "ephesians",
    "Phil": "philippians", "Col": "colossians", "1Thess": "1-thessalonians",
    "2Thess": "2-thessalonians", "1Tim": "1-timothy", "2Tim": "2-timothy",
    "Titus": "titus", "Phlm": "philemon", "Heb": "hebrews", "Jas": "james",
    "1Pet": "1-peter", "2Pet": "2-peter", "1John": "1-john", "2John": "2-john",
    "3John": "3-john", "Jude": "jude", "Rev": "revelation",
}

# --- Topographia: geographical editions (the only books built so far) ---
TOPO_SLUG = {"Josh": "joshua", "Judg": "judges", "Ruth": "ruth",
             "Jonah": "jonah", "Acts": "acts"}

# --- Annales: chronological editions, by the book each one narrates. Only the
# two LIVE editions (verified 200) — the Diatessaron/Gospel-harmony exists in the
# repo but is NOT deployed (/harmony 404s), so Gospels get no Annales link yet. ---
ANNALES_DIVIDED = {"1Kgs", "2Kgs", "2Chr"}             # the Divided Monarchy
ANNALES_PAUL = {"Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil", "Col",
                "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm"}  # Life of Paul


def reading_links(refkey: str) -> list[dict]:
    """Interpretive resources that resolve to one reading. Ordered Catena ->
    Topographia -> Annales. Each: {resource, kind, label, url}."""
    p = osis.parse_refkey(refkey)
    if not p:
        return []
    book = p["book"]
    ch = p.get("chapter") or 0
    out: list[dict] = []

    # Catena — reception history (how the church read it)
    slug = CATENA_NT_SLUG.get(book)
    if slug:
        out.append({"resource": "Catena", "kind": "reception",
                    "label": "Fathers & echoes", "url": f"{CATENA}/{slug}"})
    else:
        out.append({"resource": "Catena", "kind": "reception",
                    "label": "Index Fontium", "url": f"{CATENA}/fontium"})

    # Topographia — geography (only built books)
    tslug = TOPO_SLUG.get(book)
    if tslug:
        url = f"{TOPO}/books/{tslug}/{ch}/" if ch else f"{TOPO}/books/{tslug}/"
        out.append({"resource": "Topographia", "kind": "geography",
                    "label": "Map & places", "url": url})

    # Annales — chronology (by edition; only the two live editions)
    if book in ANNALES_DIVIDED:
        out.append({"resource": "Annales", "kind": "chronology",
                    "label": "Divided Monarchy", "url": f"{ANNALES}/divided-monarchy"})
    elif book in ANNALES_PAUL:
        out.append({"resource": "Annales", "kind": "chronology",
                    "label": "Life of Paul", "url": f"{ANNALES}/life-of-paul"})
    return out


# --- Doctrine: theme -> creed/confession document (theological application) ---
DOCS = {
    "apostles": ("The Apostles' Creed", f"{DOCTRINE}/creeds/apostles-creed/"),
    "nicene": ("The Nicene Creed", f"{DOCTRINE}/creeds/nicene-creed/"),
    "athanasian": ("The Athanasian Creed", f"{DOCTRINE}/creeds/athanasian-creed/"),
    "rules": ("Wesley's General Rules", f"{DOCTRINE}/wesleyan/general-rules/"),
    "articles": ("The Articles of Religion", f"{DOCTRINE}/wesleyan/articles-of-religion/"),
}

# Authored bridge (AI-drafted, pending Wilson's curation). Maps the day's faceted
# THEME tags to the documents that confess that theme. Themes with no strong
# creedal locus (wisdom, thanksgiving, hospitality-of-god, peace-of-god, …) are
# intentionally omitted — a thin link is worse than none.
THEME_DOCTRINE: dict[str, list[str]] = {
    "trinity": ["nicene", "athanasian"],
    "incarnation": ["nicene", "athanasian", "apostles"],
    "atonement": ["nicene", "articles"],
    "passion-and-cross": ["apostles", "nicene"],
    "resurrection-and-life": ["apostles", "nicene"],
    "ascension-and-reign": ["apostles", "nicene"],
    "holy-spirit": ["nicene", "apostles"],
    "last-things": ["apostles", "nicene"],
    "judgment": ["apostles", "nicene"],
    "church-and-unity": ["nicene", "articles"],
    "baptism": ["articles", "nicene"],
    "grace": ["articles", "rules"],
    "mercy-and-forgiveness": ["apostles", "articles"],
    "repentance": ["articles", "rules"],
    "sanctification-holiness": ["rules", "articles"],
    "faith-and-trust": ["articles"],
    "sin-and-fall": ["articles"],
    "law-and-commandment": ["articles", "rules"],
    "obedience-and-gods-will": ["rules"],
    "call-and-discipleship": ["rules"],
    "love-of-neighbor": ["rules"],
    "wealth-and-possessions": ["rules"],
    "justice": ["rules"],
    "humility-and-servanthood": ["rules"],
    "saints-and-witnesses": ["apostles"],
    "covenant": ["articles"],
    "word-of-god": ["articles"],
    "creation": ["nicene", "apostles"],
    "providence-and-care": ["apostles"],
    "messianic-hope": ["nicene"],
    "epiphany-manifestation": ["nicene"],
    "transfiguration-glory": ["nicene"],
    "kingdom-of-god": ["nicene"],
    "hope-and-promise": ["apostles"],
    "prayer-and-worship": ["rules"],
    "mission-and-witness": ["rules"],
    "idolatry": ["rules"],
    "temptation-and-testing": ["rules"],
}


def doctrine_links(themes) -> list[dict]:
    """Day-level theological application: dedup documents across the day's themes,
    each carrying which theme(s) pointed to it. Returns [{title, url, themes}]."""
    by_doc: dict[str, set] = {}
    for th in themes:
        for doc in THEME_DOCTRINE.get(th, []):
            by_doc.setdefault(doc, set()).add(th)
    out = []
    # stable doc order = order in DOCS
    for doc_key in DOCS:
        if doc_key in by_doc:
            title, url = DOCS[doc_key]
            out.append({"title": title, "url": url,
                        "themes": sorted(by_doc[doc_key])})
    return out
