// Build-time data layer. Reads the per-occasion contract files emitted by
// ../src/build_occasion.py (data/build/*.json). Used only in Server Components /
// generateStaticParams, so the filesystem access is fine under static export.
import fs from "node:fs";
import path from "node:path";

export type Reading = {
  role: string;
  ref: string;
  refKey: string;
  tags: Record<string, string[]>;
};
export type Sermon = {
  title: string | null;
  author: string | null;
  text: string | null;
  url: string | null;
  tags: string[];
  score: number;
};
export type Hymn = {
  hymnal: string | null;
  number: number | null;
  title: string | null;
  tags: string[];
  score: number;
};
export type ResourceLink = {
  resource: string;
  kind: string;
  label: string;
  url: string;
};
export type DoctrineLink = { title: string; article: string; url: string; themes: string[] };
export type SocialLink = { community: string; topic: string; url: string; themes: string[] };
export type Lenses = {
  readings: { role: string; ref: string; refKey: string; links: ResourceLink[] }[];
  doctrine: DoctrineLink[];
  social: SocialLink[];
};
export type Track = {
  label: string;
  readings: Reading[];
  sermons: Sermon[];
  hymns: Hymn[];
  lenses: Lenses;
};
export type CallRegister = {
  key: string;
  label: string;
  desc: string;
  lines: [string, string][];
};
export type Calls = { track: string; registers: CallRegister[] } | null;
export type TurnWitness = {
  author: string;
  tradition: string;
  work?: string;
  mode: "text" | "pointer";
  reading: string;
  cite?: string;
};
export type TurnDoor = {
  landing: string;
  claim: string;
  witnesses: TurnWitness[];
  say: string;
  do: string;
};
export type Turn = {
  pericope: string;
  refKey: string;
  gravity: string;
  trap: string;
  hinge: string;
  doors: TurnDoor[];
  subtract: string;
  source: string;
  status: string;
} | null;
export type Occasion = {
  occasion: { id: string; name: string | null; year: string; season: string | null };
  tracks: Record<string, Track>;
  calls: Calls;
  turn: Turn;
  lenses: unknown | null;
};

export type IndexEntry = {
  id: string;
  name: string | null;
  year: string;
  season: string | null;
  trackKeys: string[];
  readings: { role: string; ref: string }[];
  hasCalls: boolean;
  hasTurn: boolean;
};

const BUILD_DIR = path.join(process.cwd(), "..", "data", "build");

let _cache: Occasion[] | null = null;
let _index: IndexEntry[] | null = null;

export function allOccasions(): Occasion[] {
  if (_cache) return _cache;
  const files = fs
    .readdirSync(BUILD_DIR)
    .filter((f) => f.endsWith(".json") && !f.startsWith("_"))
    .sort();
  _cache = files.map(
    (f) => JSON.parse(fs.readFileSync(path.join(BUILD_DIR, f), "utf-8")) as Occasion
  );
  return _cache;
}

// Liturgically-ordered index (spine order) written by build_occasion.py --all.
export function orderedIndex(): IndexEntry[] {
  if (_index) return _index;
  const raw = fs.readFileSync(path.join(BUILD_DIR, "_index.json"), "utf-8");
  _index = (JSON.parse(raw) as { occasions: IndexEntry[] }).occasions;
  return _index;
}

export function indexByYear(year: string): IndexEntry[] {
  return orderedIndex().filter((e) => e.year.toLowerCase() === year.toLowerCase());
}

// prev / next occasion id in liturgical order, scoped to the same year.
export function neighbors(id: string): { prev: string | null; next: string | null } {
  const e = orderedIndex().find((x) => x.id === id);
  if (!e) return { prev: null, next: null };
  const yearList = indexByYear(e.year);
  const i = yearList.findIndex((x) => x.id === id);
  return {
    prev: i > 0 ? yearList[i - 1].id : null,
    next: i < yearList.length - 1 ? yearList[i + 1].id : null,
  };
}

export function getOccasion(id: string): Occasion | undefined {
  return allOccasions().find((o) => o.occasion.id === id);
}

export function occasionsByYear(year: string): Occasion[] {
  return allOccasions().filter((o) => o.occasion.year.toLowerCase() === year.toLowerCase());
}

// Liturgical season order for grouping the year view.
const SEASON_ORDER = [
  "Advent",
  "Christmas",
  "Epiphany",
  "Lent",
  "Holy Week",
  "Easter",
  "Pentecost",
  "Season after Pentecost",
];

export function seasonRank(season: string | null): number {
  if (!season) return 99;
  const i = SEASON_ORDER.indexOf(season);
  return i === -1 ? 98 : i;
}

// The build files come pre-sorted alphabetically; for the year view we keep the
// spine's own order, which is liturgical. Recover it from the master spine order
// by reading rcl.json is overkill — instead we group by season using SEASON_ORDER
// and preserve file order within a season (close enough for navigation).
export function groupBySeason(occs: Occasion[]): { season: string; items: Occasion[] }[] {
  const groups = new Map<string, Occasion[]>();
  for (const o of occs) {
    const s = o.occasion.season || "Other";
    if (!groups.has(s)) groups.set(s, []);
    groups.get(s)!.push(o);
  }
  return [...groups.entries()]
    .sort((a, b) => seasonRank(a[0]) - seasonRank(b[0]))
    .map(([season, items]) => ({ season, items }));
}

export const YEARS = ["A", "B", "C"] as const;
