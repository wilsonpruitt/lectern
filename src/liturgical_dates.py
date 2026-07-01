#!/usr/bin/env python3.11
"""Compute the calendar date of every RCL occasion for the current cycle, so the
UI can show 'where am I in the church year'. The lectionary is date-agnostic; this
resolves each occasion id to a real date:

  - Easter via the Gregorian computus; Lent/Holy Week/Eastertide/Pentecost/Trinity
    hang off it.
  - Advent/Christmas/Epiphany anchored to Christmas + Sunday math.
  - The Propers are pure date-windows ("the Sunday between D and D+6").
  - Fixed feasts (Presentation, Annunciation, All Saints, Thanksgiving, …).

Civil-year anchors per RCL year (UPDATE each 3-year cycle, like web/lib/now.ts):
Year A -> Easter 2026, B -> 2027, C -> 2028 (the cycle current as of 2026).
"""
from __future__ import annotations
import re
from datetime import date, timedelta

EASTER_YEAR = {"A": 2026, "B": 2027, "C": 2028}

# Proper N -> (month, day) start of its 7-day window; the Sunday in it is the date.
PROPER_WINDOW = {
    3: (5, 24), 4: (5, 29), 5: (6, 5), 6: (6, 12), 7: (6, 19), 8: (6, 26),
    9: (7, 3), 10: (7, 10), 11: (7, 17), 12: (7, 24), 13: (7, 31), 14: (8, 7),
    15: (8, 14), 16: (8, 21), 17: (8, 28), 18: (9, 4), 19: (9, 11), 20: (9, 18),
    21: (9, 25), 22: (10, 2), 23: (10, 9), 24: (10, 16), 25: (10, 23),
    26: (10, 30), 27: (11, 6), 28: (11, 13), 29: (11, 20),
}


def easter(year: int) -> date:
    a = year % 19; b = year // 100; c = year % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30; i = c // 4; k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31; day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def sunday_on_or_before(d: date) -> date:
    return d - timedelta(days=(d.weekday() + 1) % 7)  # weekday: Mon=0 .. Sun=6


def sunday_on_or_after(d: date) -> date:
    return d + timedelta(days=(6 - d.weekday()) % 7)


def nth_weekday(year, month, weekday, n):  # weekday Mon=0..Sun=6
    d = date(year, month, 1)
    first = d + timedelta(days=(weekday - d.weekday()) % 7)
    return first + timedelta(days=7 * (n - 1))


def ordinal(s: str) -> int:
    return {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
            "sixth": 6, "seventh": 7}.get(s, 0)


def occasion_date(stem: str, ey: int) -> date | None:
    """stem = occasion id with the -a/-b/-c stripped. ey = Easter civil year."""
    cy = ey - 1                                 # Advent/Christmas civil year
    e = easter(ey)
    palm = e - timedelta(days=7)
    ash = e - timedelta(days=46)
    pentecost = e + timedelta(days=49)

    # --- Propers (date-window Sundays) ---
    m = re.match(r"proper-(\d+)-", stem) or re.match(r"reign-of-christ-proper-(\d+)-", stem)
    if m:
        n = int(m.group(1))
        mo, dy = PROPER_WINDOW.get(n, (None, None))
        if mo:
            return sunday_on_or_after(date(ey, mo, dy))
        return None

    # --- Advent (cy, Nov-Dec): Advent 1 = Sunday in [Nov 27, Dec 3] ---
    m = re.match(r"(first|second|third|fourth)-sunday-of-advent", stem)
    if m:
        advent1 = sunday_on_or_after(date(cy, 11, 27))
        return advent1 + timedelta(days=7 * (ordinal(m.group(1)) - 1))

    # --- Christmas / Nativity (cy Dec) ---
    if stem.startswith("nativity-of-the-lord-proper-i"):
        return date(cy, 12, 24) if stem.endswith("proper-i") else date(cy, 12, 25)
    if stem == "first-sunday-after-christmas-day":
        return sunday_on_or_after(date(cy, 12, 26))
    if stem in ("holy-name-of-jesus", "new-year-s-day"):
        return date(ey, 1, 1)
    if stem in ("second-sunday-after-christmas-day", "second-sunday-after-thechristmas"):
        s = sunday_on_or_after(date(cy, 12, 26)) + timedelta(days=7)
        return s if s < date(ey, 1, 6) else None

    # --- Epiphany season (ey, Jan-Feb) ---
    if stem == "epiphany-of-the-lord":
        return date(ey, 1, 6)
    baptism = sunday_on_or_after(date(ey, 1, 7))  # Sunday after Epiphany
    if stem == "baptism-of-the-lord":
        return baptism
    if stem == "presentation-of-the-lord":
        return date(ey, 2, 2)
    if stem == "transfiguration-sunday":          # last Sunday before Ash Wed
        return sunday_on_or_before(ash - timedelta(days=1))
    m = re.match(r"(first|second|third|fourth|fifth|sixth|seventh)-sunday-after-the-epiphany", stem)
    if m:
        return baptism + timedelta(days=7 * ordinal(m.group(1)))

    # --- Lent / Holy Week / Triduum ---
    if stem == "ash-wednesday":
        return ash
    m = re.match(r"(first|second|third|fourth|fifth)-sunday-in-lent", stem)
    if m:
        return e - timedelta(days=7 * (6 - ordinal(m.group(1))))  # Lent1 = E-42 .. Lent5 = E-14
    if stem in ("liturgy-of-the-palms", "liturgy-of-the-passion"):
        return palm
    if stem == "monday-of-holy-week":
        return e - timedelta(days=6)
    if stem == "tuesday-of-holy-week":
        return e - timedelta(days=5)
    if stem == "wednesday-of-holy-week":
        return e - timedelta(days=4)
    if stem == "maundy-thursday":
        return e - timedelta(days=3)
    if stem == "good-friday":
        return e - timedelta(days=2)
    if stem in ("holy-saturday", "easter-vigil"):
        return e - timedelta(days=1)

    # --- Easter season ---
    if stem in ("resurrection-of-the-lord", "easter-evening"):
        return e
    m = re.match(r"(second|third|fourth|fifth|sixth|seventh)-sunday-of-easter", stem)
    if m:
        return e + timedelta(days=7 * (ordinal(m.group(1)) - 1))
    if stem == "ascension-of-the-lord":
        return e + timedelta(days=39)
    if stem == "day-of-pentecost":
        return pentecost
    if stem == "trinity-sunday":
        return pentecost + timedelta(days=7)

    # --- Fixed feasts ---
    if stem == "annunciation-of-the-lord":
        return date(ey, 3, 25)
    if stem == "visitation-of-mary-to-elizabeth":
        return date(ey, 5, 31)
    if stem == "holy-cross":
        return date(ey, 9, 14)
    if stem == "all-saints-day":
        return date(ey, 11, 1)
    if stem == "canadian-thanksgiving-day":
        return nth_weekday(ey, 10, 0, 2)          # 2nd Monday of October
    if stem == "thanksgiving-day-usa":
        return nth_weekday(ey, 11, 3, 4)          # 4th Thursday of November
    return None


def all_dates() -> dict:
    """{occasion_id: {'date': 'YYYY-MM-DD', 'display': 'Jul 5, 2026'}}."""
    import json
    from pathlib import Path
    spine = json.loads((Path.home() / "reception-corpus" / "data" / "rcl.json").read_text())
    out = {}
    for o in spine["occasions"]:
        oid = o["id"]
        year = o["year"]
        stem = re.sub(r"-[abc]$", "", oid)
        d = occasion_date(stem, EASTER_YEAR[year])
        if d:
            out[oid] = {"date": d.isoformat(),
                        "display": f"{d.strftime('%b')} {d.day}, {d.year}"}
    return out


if __name__ == "__main__":
    d = all_dates()
    print(f"resolved {len(d)} occasion dates")
    for oid in ["first-sunday-of-advent-a", "nativity-of-the-lord-proper-iii-a",
                "epiphany-of-the-lord-a", "ash-wednesday-a", "resurrection-of-the-lord-a",
                "day-of-pentecost-a", "proper-8-13-a", "proper-9-14-a",
                "proper-23-28-a", "reign-of-christ-proper-29-34-a"]:
        print(f"  {oid:34} {d.get(oid, {}).get('display','—')}")
