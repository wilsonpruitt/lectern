// "Where are we in the church year?" — drives the landing's This-Sunday strip.
//
// Lectern is a static build, so there is no live clock; instead we anchor to a
// known Sunday + its date and advance weekly from there through the current
// year's index at BUILD time. This keeps "this Sunday" roughly current through an
// Ordinary-Time run without a full liturgical-calendar engine. When the season
// turns (or the year cycles A->B->C), update ANCHOR — or wire a computus later.
import { type IndexEntry, indexByYear } from "./data";

export const ANCHOR = {
  year: "A",
  id: "proper-8-13-a", // last observed Sunday (Matt 10:40-42)
  date: "2026-06-28",
};

const WEEK = 7 * 24 * 60 * 60 * 1000;

/** The upcoming Sunday + the next several, in liturgical order, for ANCHOR.year. */
export function weeksAhead(count = 5, nowISO?: string): IndexEntry[] {
  const items = indexByYear(ANCHOR.year);
  const i = items.findIndex((e) => e.id === ANCHOR.id);
  if (i < 0) return items.slice(0, count);
  const now = nowISO ? Date.parse(nowISO) : Date.now();
  const elapsed = Math.max(0, Math.floor((now - Date.parse(ANCHOR.date)) / WEEK));
  // the most recent past Sunday is anchor+elapsed; "this Sunday" is the next one
  const start = Math.min(i + elapsed + 1, items.length - 1);
  return items.slice(start, start + count);
}
