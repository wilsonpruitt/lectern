// "Where are we in the church year?" — drives the landing's This-Sunday strip.
// Now exact: each occasion carries a real date (baked by src/liturgical_dates.py
// for the current cycle), so we just pick the next upcoming occasion by date.
// CURRENT.year = the RCL year now in progress — bump it (and the EASTER_YEAR map
// in src/liturgical_dates.py) when the cycle turns A->B->C.
//
// This module stays filesystem-free (the IndexEntry import is type-only) so the
// client ThisSunday strip can share pickAhead — under static export a server-side
// `new Date()` freezes at build time, so the browser has to do the picking.
import type { IndexEntry } from "./data";

export const CURRENT = { year: "A" };

/** The upcoming occasion + the next several, out of an already-dated list. */
export function pickAhead(dated: IndexEntry[], count = 5, nowISO?: string): IndexEntry[] {
  const today = (nowISO ?? new Date().toISOString()).slice(0, 10);
  const items = [...dated].sort((a, b) => a.date!.localeCompare(b.date!));
  if (!items.length) return [];
  const i = items.findIndex((e) => e.date! >= today);
  const start = i === -1 ? Math.max(0, items.length - count) : i;
  return items.slice(start, start + count);
}
