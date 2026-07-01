// Build-time data layer for the Greek study tool. Reads the static API tree synced by
// ../src/build_greek.py (web/public/api/greek/**). Used in Server Components / generateStaticParams,
// so filesystem access is fine under static export. Per-lemma lexicon entries are NOT read here —
// the client fetches them lazily from /api/greek/lex/<enc(lexKey)>.json on word click.
import fs from "node:fs";
import path from "node:path";

const GREEK_DIR = path.join(process.cwd(), "public", "api", "greek");

export type GreekWord = {
  i: number;
  text: string;      // surface form with editorial marks
  word: string;      // surface form, marks stripped
  lemma: string;     // dictionary citation form
  lexKey: string;    // join key to the lexicon (and the lazy-fetch filename, url-encoded)
  foldKey: string;
  pos: string;       // raw MorphGNT POS code
  parse: string;     // raw 8-slot parse code
  morph: string;     // human label, e.g. "noun · nominative singular feminine"
  gloss?: string;    // concise classical gloss (attached from short-glosses.json)
};
export type GreekVerse = {
  refKey: string;
  refDisplay: string;
  chapter: number;
  verse: number;
  words: GreekWord[];
};
export type BookMeta = { code: string; name: string; verseCount: number; chapters: Record<string, number> };
type Index = { books: BookMeta[]; refKeys: string[] };

let _index: Index | null = null;
let _glosses: Record<string, string> | null = null;
const _books = new Map<string, GreekVerse[]>();

function readJSON<T>(p: string): T {
  return JSON.parse(fs.readFileSync(p, "utf-8")) as T;
}

export function greekIndex(): Index {
  if (!_index) _index = readJSON<Index>(path.join(GREEK_DIR, "index.json"));
  return _index;
}

export function shortGlosses(): Record<string, string> {
  if (!_glosses) _glosses = readJSON<Record<string, string>>(path.join(GREEK_DIR, "short-glosses.json"));
  return _glosses;
}

function bookOf(refKey: string): string {
  return refKey.split(".")[0];
}

function loadBook(code: string): GreekVerse[] {
  let v = _books.get(code);
  if (!v) {
    const d = readJSON<{ verses: GreekVerse[] }>(path.join(GREEK_DIR, "books", `${code}.json`));
    v = d.verses;
    _books.set(code, v);
  }
  return v;
}

export function allRefKeys(): string[] {
  return greekIndex().refKeys;
}

/** A verse with its words' concise glosses attached (for inline display). */
export function getVerse(refKey: string): GreekVerse | undefined {
  const verses = loadBook(bookOf(refKey));
  const v = verses.find((x) => x.refKey === refKey);
  if (!v) return undefined;
  const g = shortGlosses();
  return { ...v, words: v.words.map((w) => ({ ...w, gloss: g[w.lexKey] })) };
}

/** Previous / next verse within the same book (for verse-to-verse nav). */
export function verseNeighbors(refKey: string): { prev: string | null; next: string | null } {
  const verses = loadBook(bookOf(refKey));
  const i = verses.findIndex((x) => x.refKey === refKey);
  return {
    prev: i > 0 ? verses[i - 1].refKey : null,
    next: i >= 0 && i < verses.length - 1 ? verses[i + 1].refKey : null,
  };
}
