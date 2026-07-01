"use client";
// The merged Greek study view: BibleHub-style word-by-word parsing (left) + Logeion-style
// classical lexicon (right). Parsing + inline glosses are baked into the page; the full
// Middle Liddell / LSJ entry for a word is lazy-fetched from /api/greek/lex/<enc(lexKey)>.json
// on click. Classical lexica only — no Koiné/Bible dictionary.
import { useState, useCallback, useRef } from "react";
import type { GreekVerse as Verse, GreekWord } from "@/lib/greek";

// Reading form of a word: MorphGNT's surface text keeps punctuation (·, comma, period) but also
// carries SBL apparatus sigla (⸀⸂⸃…, U+2E00–U+2E1F). Strip the sigla so the verse reads plain.
function readingText(text: string): string {
  return text.replace(/[⸀-⸟]/g, "");
}

// ASCII-safe filename slug for a lexKey — hex of its NFC-UTF8 bytes. Must match
// reception-corpus greek.lex_slug(): Greek filenames don't survive Vercel static routing.
function lexSlug(lexKey: string): string {
  const bytes = new TextEncoder().encode(lexKey.normalize("NFC"));
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

type LexEntry = {
  lexKey: string;
  headword: string;
  lemma: string | null;
  midliddell: { gloss: string; html: string } | null;
  lsj: { gloss: string; html: string } | null;
};

export default function GreekVerse({ verse }: { verse: Verse }) {
  const [sel, setSel] = useState<number | null>(null);
  const [entry, setEntry] = useState<LexEntry | null>(null);
  const [loading, setLoading] = useState(false);
  const [showLsj, setShowLsj] = useState(false);
  const cache = useRef<Map<string, LexEntry | null>>(new Map());

  const selectWord = useCallback(async (w: GreekWord) => {
    setSel(w.i);
    setShowLsj(false);
    setEntry(null);
    if (!w.gloss && !w.lexKey) return;
    const key = w.lexKey;
    if (cache.current.has(key)) {
      setEntry(cache.current.get(key)!);
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`/api/greek/lex/${lexSlug(key)}.json`);
      const data = res.ok ? ((await res.json()) as LexEntry) : null;
      cache.current.set(key, data);
      setEntry(data);
    } catch {
      cache.current.set(key, null);
      setEntry(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const selWord = sel !== null ? verse.words.find((w) => w.i === sel) : undefined;

  return (
    <div className="gk-layout">
      {/* Plain reading text — the Greek reads as running prose; parse + gloss stay hidden
          until a word is tapped (revealed in the panel). Not an interlinear. */}
      <p className="gk-reading">
        {verse.words.map((w, idx) => (
          <span key={w.i}>
            {idx > 0 && " "}
            <button
              className={`gk-word${sel === w.i ? " sel" : ""}`}
              onClick={() => selectWord(w)}
            >
              {readingText(w.text)}
            </button>
          </span>
        ))}
      </p>

      <aside className="gk-panel">
        {!selWord && <p className="gk-hint">Tap a word for its classical lexicon entry.</p>}
        {selWord && (
          <div className="gk-entry">
            <div className="gk-entry-head">
              <span className="gk-lemma">{selWord.lemma}</span>
              <span className="gk-entry-morph">{selWord.morph}</span>
            </div>
            {loading && <p className="gk-hint">Loading…</p>}
            {!loading && !entry && (
              <p className="gk-hint gk-nomatch">
                Not in the classical lexicon — typically a proper noun or a distinctively biblical
                word (no LSJ / Middle Liddell entry).
              </p>
            )}
            {!loading && entry && (
              <>
                {entry.midliddell && (
                  <section className="gk-source">
                    <h4>Middle Liddell</h4>
                    <div className="gk-lex" dangerouslySetInnerHTML={{ __html: entry.midliddell.html }} />
                  </section>
                )}
                {entry.lsj && (
                  <section className="gk-source">
                    <button className="gk-toggle" onClick={() => setShowLsj((v) => !v)}>
                      {showLsj ? "▾" : "▸"} Liddell-Scott-Jones (full)
                    </button>
                    {showLsj && (
                      <div className="gk-lex" dangerouslySetInnerHTML={{ __html: entry.lsj.html }} />
                    )}
                    {!showLsj && entry.lsj.gloss && (
                      <p className="gk-lsj-teaser">{entry.lsj.gloss}</p>
                    )}
                  </section>
                )}
                {!entry.midliddell && !entry.lsj && (
                  <p className="gk-hint gk-nomatch">No classical entry found.</p>
                )}
              </>
            )}
          </div>
        )}
      </aside>
    </div>
  );
}
