// Build-time data layer. Reads the per-occasion contract files emitted by
// ../src/build_occasion.py (data/build/*.json). Used only in Server Components /
// generateStaticParams, so the filesystem access is fine under static export.
import fs from "node:fs";
import path from "node:path";

export type WesleyNote = {
  chapter: number;
  v_start: number;
  v_end: number;
  text: string;
};
export type Gloss = {
  chapter: number;
  v_start: number;
  v_end: number;
  text: string;
  anchor: string | null;
};
export type Reading = {
  role: string;
  ref: string;
  refKey: string;
  tags: Record<string, string[]>;
  notes: WesleyNote[];
  glossa: Gloss[];
  glossaBookCovered: boolean;
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

// --- Phase 3: Catena echoes / Annales chronology / Topographia map, inline in Lenses ---
export type Echo = { source: string; type: string; confidence: string; text: string; note: string };
export type CatenaPericope = { pericopeId: string; ref: string; echoes: Echo[] };
export type CatenaOccurrence = {
  refKey: string;
  refDisplay: string;
  book: string;
  slug: string;
  pericopeId: string;
  type: string;
  confidence: string;
  url: string;
};
export type CatenaSource = { source: string; occurrences: CatenaOccurrence[] };
export type CatenaEchoes =
  | { kind: "nt"; pericopes: CatenaPericope[]; attribution: string }
  | { kind: "ot"; sources: CatenaSource[]; attribution: string };

export type AnnalesSpan = {
  label: string;
  group: string | null;
  lane: string | null;
  start: number;
  end: number | null;
  length: string | null;
  ref: string;
  note: string | null;
};
export type AnnalesEvent = {
  year: number;
  label: string;
  ref: string;
  kind: string | null;
  approx: boolean | null;
  note: string | null;
};
export type HarmonyEpisode = {
  title: string | null;
  section: string | null;
  refs: Record<string, string>;
  note: string | null;
};
export type AnnalesEdition = {
  edition: string;
  editionUrl: string;
  spans?: AnnalesSpan[];
  events?: AnnalesEvent[];
  harmony?: HarmonyEpisode[];
};
export type Chronology = { editions: AnnalesEdition[]; note: string };

export type MapPlace = {
  key: string;
  name: string;
  coords: [number, number];
  tier: string;
  id: string | null;
};
export type PlacesMapData = {
  chapterUrl: string;
  title: string | null;
  view: { center: [number, number]; zoom: number } | null;
  route: string[] | null;
  approxChapter: number | null;
  places: MapPlace[];
};

export type Lenses = {
  readings: {
    role: string;
    ref: string;
    refKey: string;
    links: ResourceLink[];
    echoes: CatenaEchoes | null;
    chronology: Chronology | null;
    map: PlacesMapData | null;
  }[];
  doctrine: DoctrineLink[];
  social: SocialLink[];
};
export type PraiseSong = {
  title: string;
  timesUsed: number | null;
  frequency: string | null;
  pd: boolean;
  url: string;
  tags: string[];
  score: number;
};
export type Track = {
  label: string;
  readings: Reading[];
  sermons: Sermon[];
  hymns: Hymn[];
  praise: PraiseSong[];
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
export type TurnSynthesis = { convergence: string; claim: string; here: string };
// v2 (Phase 4a): the Gospel doors are shared across tracks; gravity/synthesis and
// an optional set of attested first-reading doors are PER TRACK. A track present
// with only firstReading (no gravity) means it hasn't been authored yet -- render
// that quietly, don't hide the tab. Key is a track id ("complementary",
// "semicontinuous") or "single" for occasions with no dual tracks.
export type TurnFirstReading = { ref: string; refKey: string; refKeys?: string[]; doors: TurnDoor[] };
export type TurnTrack = {
  firstReading: TurnFirstReading;
  gravity?: string;
  synthesis?: TurnSynthesis;
};
export type Turn = {
  pericope: string;
  refKey: string;
  trap: string;
  hinge: string;
  doors: TurnDoor[];
  tracks: Record<string, TurnTrack>;
  subtract: string;
  source: string;
  status: string;
} | null;
export type Occasion = {
  occasion: {
    id: string;
    name: string | null;
    year: string;
    season: string | null;
    date?: string;
    display?: string;
  };
  tracks: Record<string, Track>;
  calls: Calls;
  turn: Turn;
  lenses: unknown | null;
};

export type SeriesBeat = { label: string; note?: string | null };
export type SeriesMembership = {
  id: string;
  role: string;
  roleLabel: string;
  book: string;
  week: number;
  of: number;
  prev: string | null;
  next: string | null;
  arc?: string | null;
  beat?: SeriesBeat | null;
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
  hasTurnTracks: string[];
  series: SeriesMembership[];
  date?: string;
  display?: string;
};
export type Series = {
  id: string;
  role: string;
  roleLabel: string;
  book: string;
  bookCode: string;
  weeks: number;
  occasions: string[];
  from: string | null;
  to: string | null;
  arc?: string | null;
  beats?: { from: number; to: number; label: string; note?: string | null }[];
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

// Native series (the founding thesis) written by build_occasion.py --all.
let _series: Record<string, Series[]> | null = null;
export function seriesByYear(year: string): Series[] {
  if (!_series) {
    _series = JSON.parse(
      fs.readFileSync(path.join(BUILD_DIR, "_series.json"), "utf-8")
    ) as Record<string, Series[]>;
  }
  return _series[year.toUpperCase()] ?? [];
}

export function indexEntry(id: string): IndexEntry | undefined {
  return orderedIndex().find((e) => e.id === id);
}

export const YEARS = ["A", "B", "C"] as const;
