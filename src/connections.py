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
import json
import re
import sys
from pathlib import Path

RECEPTION_SRC = Path.home() / "reception-corpus" / "src"
sys.path.insert(0, str(RECEPTION_SRC))
import osis  # noqa: E402  (parse_refkey -> {book, chapter, ...})

# Catena's reader supports a documented deep-link: /<book>#p-<pericope-id> scrolls
# to and flags that pericope. We resolve the day's reading to its pericope id by
# matching against ~/catena/data/<slug>.json (loaded lazily, build-time only).
_CATENA_DATA = Path.home() / "catena" / "data"
_catena_cache: dict = {}


def _catena_pericope_id(slug, chapter, v1, v2):
    if slug not in _catena_cache:
        f = _CATENA_DATA / f"{slug}.json"
        _catena_cache[slug] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    book = _catena_cache[slug]
    if not book:
        return None
    fallback = None
    for per in book.get("pericopes", []):
        if per.get("ch") != chapter:
            continue
        m = re.match(r"\d+:(\d+)(?:-(\d+))?", per.get("ref", ""))
        if not m:
            fallback = fallback or per.get("id")
            continue
        pv1 = int(m.group(1))
        pv2 = int(m.group(2)) if m.group(2) else pv1
        if pv1 <= v2 and v1 <= pv2:          # verse-range overlap
            return per.get("id")
    return fallback

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

# --- Annales: chronological editions, by the book each one narrates. All three
# verified live (200): /divided-monarchy, /life-of-paul, and the Gospel harmony at
# /harmony/diatessaron (deployed 2026-06-30; note the route is /harmony/<slug>). ---
ANNALES_DIVIDED = {"1Kgs", "2Kgs", "2Chr"}             # the Divided Monarchy
ANNALES_PAUL = {"Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil", "Col",
                "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm"}  # Life of Paul
ANNALES_GOSPEL = {"Matt", "Mark", "Luke", "John"}      # the Diatessaron harmony


def reading_links(refkey: str) -> list[dict]:
    """Interpretive resources that resolve to one reading. Ordered Catena ->
    Topographia -> Annales. Each: {resource, kind, label, url}."""
    p = osis.parse_refkey(refkey)
    if not p:
        return []
    book = p["book"]
    ch = p.get("chapter") or 0
    out: list[dict] = []

    # Catena — reception history (how the church read it); deep-link to the pericope
    slug = CATENA_NT_SLUG.get(book)
    if slug:
        pid = _catena_pericope_id(slug, ch, p["v_start"],
                                  p.get("v_end_true") or p["v_start"]) if ch else None
        url = f"{CATENA}/{slug}#p-{pid}" if pid else f"{CATENA}/{slug}"
        out.append({"resource": "Catena", "kind": "reception",
                    "label": "Fathers & echoes", "url": url})
    else:
        out.append({"resource": "Catena", "kind": "reception",
                    "label": "Index Fontium", "url": f"{CATENA}/fontium"})

    # Topographia — geography (only built books)
    tslug = TOPO_SLUG.get(book)
    if tslug:
        url = f"{TOPO}/books/{tslug}/{ch}/" if ch else f"{TOPO}/books/{tslug}/"
        out.append({"resource": "Topographia", "kind": "geography",
                    "label": "Map & places", "url": url})

    # Annales — chronology (by edition)
    if book in ANNALES_GOSPEL:
        out.append({"resource": "Annales", "kind": "chronology",
                    "label": "Gospel harmony", "url": f"{ANNALES}/harmony/diatessaron"})
    elif book in ANNALES_DIVIDED:
        out.append({"resource": "Annales", "kind": "chronology",
                    "label": "Divided Monarchy", "url": f"{ANNALES}/divided-monarchy"})
    elif book in ANNALES_PAUL:
        out.append({"resource": "Annales", "kind": "chronology",
                    "label": "Life of Paul", "url": f"{ANNALES}/life-of-paul"})
    return out


# --- Doctrine: theme -> SPECIFIC creed clause / confession article (deep-link) ---
# doctrine.wrootpress.com has a per-phrase route /<family>/<doc>/<phrase-slug>/ —
# so we link straight to the relevant article, not the document landing.
DOC_FAMILY = {
    "apostles-creed": "creeds", "nicene-creed": "creeds", "athanasian-creed": "creeds",
    "general-rules": "wesleyan", "articles-of-religion": "wesleyan",
}
DOC_TITLE = {
    "apostles-creed": "Apostles' Creed", "nicene-creed": "Nicene Creed",
    "athanasian-creed": "Athanasian Creed", "general-rules": "General Rules",
    "articles-of-religion": "Articles of Religion",
}

# Authored bridge (AI-drafted, Wilson curates): theme -> [(doc, phrase_slug, article
# label)] — the specific clause/article that confesses the theme. Phrase slugs are
# the real doctrine-site routes (verified from ~/doctrine annotations).
THEME_DOCTRINE: dict[str, list[tuple]] = {
    "trinity": [("nicene-creed", "of-one-being-with-the-father", "of one Being with the Father"),
                ("athanasian-creed", "one-god-in-trinity", "one God in Trinity")],
    "incarnation": [("nicene-creed", "incarnate-of-the-virgin-mary", "incarnate of the Virgin Mary"),
                    ("apostles-creed", "born-of-the-virgin-mary", "born of the Virgin Mary")],
    "atonement": [("articles-of-religion", "article-20-of-the-one-oblation-of-christ", "Art. XX, the One Oblation of Christ"),
                  ("nicene-creed", "crucified-suffered-buried", "crucified, suffered, buried")],
    "passion-and-cross": [("apostles-creed", "was-crucified", "was crucified"),
                          ("nicene-creed", "crucified-suffered-buried", "crucified, suffered, buried")],
    "resurrection-and-life": [("apostles-creed", "the-resurrection-of-the-body", "the resurrection of the body"),
                              ("nicene-creed", "on-the-third-day-he-rose", "on the third day he rose")],
    "ascension-and-reign": [("apostles-creed", "he-ascended-into-heaven", "he ascended into heaven"),
                            ("nicene-creed", "ascended-into-heaven", "ascended into heaven")],
    "holy-spirit": [("nicene-creed", "i-believe-in-the-holy-spirit", "the Holy Spirit, the giver of life"),
                    ("articles-of-religion", "article-4-of-the-holy-ghost", "Art. IV, the Holy Ghost")],
    "last-things": [("apostles-creed", "and-the-life-everlasting", "the life everlasting"),
                    ("nicene-creed", "the-life-of-the-world-to-come", "the life of the world to come")],
    "judgment": [("apostles-creed", "from-thence-he-shall-come-to-judge", "he shall come to judge"),
                 ("nicene-creed", "will-come-again-to-judge", "will come again to judge")],
    "church-and-unity": [("nicene-creed", "one-holy-catholic-and-apostolic-church", "one holy catholic and apostolic Church"),
                         ("articles-of-religion", "article-13-of-the-church", "Art. XIII, the Church")],
    "baptism": [("articles-of-religion", "article-17-of-baptism", "Art. XVII, Baptism"),
                ("nicene-creed", "one-baptism-for-the-forgiveness-of-sins", "one baptism for the forgiveness of sins")],
    "grace": [("articles-of-religion", "article-9-of-the-justification-of-man", "Art. IX, the Justification of Man"),
              ("articles-of-religion", "article-8-of-free-will", "Art. VIII, Free Will")],
    "mercy-and-forgiveness": [("apostles-creed", "the-forgiveness-of-sins", "the forgiveness of sins")],
    "repentance": [("articles-of-religion", "article-12-of-sin-after-justification", "Art. XII, Sin After Justification")],
    "sanctification-holiness": [("articles-of-religion", "article-26-of-sanctification", "Of Sanctification"),
                                ("general-rules", "evidenced-by-its-fruits", "evidenced by its fruits")],
    "faith-and-trust": [("articles-of-religion", "article-9-of-the-justification-of-man", "Art. IX, justification by faith")],
    "sin-and-fall": [("articles-of-religion", "article-7-of-original-or-birth-sin", "Art. VII, Original Sin")],
    "law-and-commandment": [("general-rules", "first-rule-do-no-harm", "do no harm"),
                            ("articles-of-religion", "article-6-of-the-old-testament", "Art. VI, the Old Testament")],
    "obedience-and-gods-will": [("general-rules", "second-rule-do-good", "do good")],
    "call-and-discipleship": [("general-rules", "the-one-condition", "the one condition")],
    "love-of-neighbor": [("general-rules", "doing-good-to-bodies-and-souls", "doing good to bodies and souls")],
    "wealth-and-possessions": [("articles-of-religion", "article-24-of-christian-mens-goods", "Art. XXIV, Christian Men's Goods")],
    "justice": [("general-rules", "the-slaveholding-clause", "the slaveholding clause"),
                ("general-rules", "first-rule-do-no-harm", "do no harm")],
    "humility-and-servanthood": [("general-rules", "second-rule-do-good", "do good")],
    "saints-and-witnesses": [("apostles-creed", "the-communion-of-saints", "the communion of saints")],
    "covenant": [("articles-of-religion", "article-6-of-the-old-testament", "Art. VI, the Old Testament")],
    "word-of-god": [("articles-of-religion", "article-5-of-the-sufficiency-of-the-holy-scriptures", "Art. V, Sufficiency of Scripture")],
    "creation": [("nicene-creed", "maker-of-heaven-and-earth", "maker of heaven and earth"),
                 ("apostles-creed", "creator-of-heaven-and-earth", "creator of heaven and earth")],
    "providence-and-care": [("apostles-creed", "the-father-almighty", "the Father almighty")],
    "messianic-hope": [("nicene-creed", "eternally-begotten-of-the-father", "eternally begotten of the Father")],
    "epiphany-manifestation": [("nicene-creed", "god-from-god-light-from-light", "God from God, Light from Light")],
    "transfiguration-glory": [("nicene-creed", "god-from-god-light-from-light", "God from God, Light from Light")],
    "kingdom-of-god": [("nicene-creed", "the-life-of-the-world-to-come", "the life of the world to come")],
    "hope-and-promise": [("apostles-creed", "and-the-life-everlasting", "the life everlasting")],
    "prayer-and-worship": [("general-rules", "third-rule-the-ordinances-of-god", "the ordinances of God")],
    "mission-and-witness": [("general-rules", "doing-good-to-bodies-and-souls", "doing good")],
    "idolatry": [("general-rules", "the-catalog-of-harms", "the catalog of harms")],
    "temptation-and-testing": [("general-rules", "first-rule-do-no-harm", "do no harm")],
}


def doctrine_links(themes) -> list[dict]:
    """Theological application: dedup specific articles across the day's themes.
    Returns [{title (document), article, url, themes}] deep-linked to the clause."""
    by_art: dict[tuple, set] = {}
    order: list[tuple] = []
    for th in sorted(themes):
        for doc, phrase, label in THEME_DOCTRINE.get(th, []):
            key = (doc, phrase, label)
            if key not in by_art:
                by_art[key] = set()
                order.append(key)
            by_art[key].add(th)
    out = []
    for doc, phrase, label in order:
        out.append({
            "title": DOC_TITLE[doc], "article": label,
            "url": f"{DOCTRINE}/{DOC_FAMILY[doc]}/{doc}/{phrase}/",
            "themes": sorted(by_art[(doc, phrase, label)]),
        })
    return out


# --- UMC Social Principles (2024) — social-ethical application, deep-linked ---
# The official revised Social Principles are published BY TOPIC on umc.org, each
# with an in-page anchor — so we link to the specific position (not a landing, and
# not the © BoD prose). theme -> [(community, anchor, topic label)].
SOCIAL_PAGE = {
    "natural": ("Community of All Creation", "https://www.umc.org/en/content/social-principles-the-natural-world"),
    "economic": ("The Economic Community", "https://www.umc.org/en/content/social-principles-the-economic-community"),
    "social": ("The Social Community", "https://www.umc.org/en/content/social-principles-the-social-community"),
    "political": ("The Political Community", "https://www.umc.org/en/content/social-principles-the-political-community"),
    "creed": ("Our Social Creed", "https://www.umc.org/en/content/our-social-creed"),
}

# Authored bridge (AI-drafted, Wilson curates): theme -> [(community, anchor, label)].
# Anchors verified from the umc.org community pages.
THEME_SOCIAL: dict[str, list[tuple]] = {
    "creation": [("natural", "stewardship-of-creation", "Stewardship of Creation"),
                 ("natural", "global-warming", "Global Warming & Climate Change")],
    "providence-and-care": [("natural", "creatures", "Caring for All Creatures")],
    "wealth-and-possessions": [("economic", "poverty", "Poverty & Income Inequality"),
                               ("economic", "consumerism", "Responsible Consumerism")],
    "justice": [("political", "basic-rights", "Basic Rights & Freedoms"),
                ("economic", "poverty", "Poverty & Income Inequality")],
    "love-of-neighbor": [("social", "racism", "Racism, Ethnocentrism & Tribalism"),
                         ("political", "migrants", "Migrants, Immigrants & Refugees")],
    "mercy-and-forgiveness": [("political", "restorative", "Restorative Justice"),
                              ("political", "criminal-justice", "Criminal Justice")],
    "humility-and-servanthood": [("economic", "work", "The Dignity of Work")],
    "hospitality-of-god": [("political", "migrants", "Migrants, Immigrants & Refugees")],
    "peace-of-god": [("political", "war", "War & Military Service")],
    "law-and-commandment": [("political", "civil-disobedience", "Civil Disobedience")],
    "suffering-and-endurance": [("political", "health-care", "Health Care")],
    "idolatry": [("economic", "consumerism", "Responsible Consumerism")],
    "prayer-and-worship": [("economic", "sabbath", "Sabbath & Renewal Time")],
    "thanksgiving": [("economic", "sabbath", "Sabbath & Renewal Time")],
}


def social_principles_links(themes) -> list[dict]:
    """Social-ethical application: dedup specific umc.org positions across the day's
    themes. Returns [{community, topic, url, themes}] deep-linked to the anchor."""
    by_pos: dict[tuple, set] = {}
    order: list[tuple] = []
    for th in sorted(themes):
        for comm, anchor, label in THEME_SOCIAL.get(th, []):
            key = (comm, anchor, label)
            if key not in by_pos:
                by_pos[key] = set()
                order.append(key)
            by_pos[key].add(th)
    out = []
    for comm, anchor, label in order:
        community, page = SOCIAL_PAGE[comm]
        url = f"{page}#{anchor}" if anchor else page
        out.append({"community": community, "topic": label, "url": url,
                    "themes": sorted(by_pos[(comm, anchor, label)])})
    return out


# --- Wesley sermons -> their text at resourceumc.org (numeric index) ---
# URL pattern (verified): /en/content/sermon-<N>-<title-slug>. Built only for the
# numbered standard sermons (id jw-sermon-NNN) with a real title.
def wesley_sermon_url(sermon_id: str | None, title: str | None) -> str | None:
    if not sermon_id or not title:
        return None
    m = re.match(r"jw-sermon-0*(\d+)$", sermon_id)
    if not m or re.match(r"(?i)sermon\s*\d+$", title.strip()):
        return None  # named-id or untitled "Sermon N" — no reliable slug
    n = int(m.group(1))
    slug = re.sub(r"[^a-z0-9]+", "-",
                  title.lower().replace("'", "").replace("’", "")).strip("-")
    return f"https://www.resourceumc.org/en/content/sermon-{n}-{slug}"
