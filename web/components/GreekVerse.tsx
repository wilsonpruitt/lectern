"use client";
// The merged Greek study view: BibleHub-style word-by-word parsing (left) + Logeion-style
// classical lexicon (right). Parsing + inline glosses are baked into the page; the full
// Middle Liddell / LSJ entry for a word is lazy-fetched from /api/greek/lex/<enc(lexKey)>.json
// on click. Classical lexica only — no Koiné/Bible dictionary.
import { useState, useCallback, useRef } from "react";
import type { GreekVerse as Verse, GreekWord } from "@/lib/greek";

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
      const res = await fetch(`/api/greek/lex/${encodeURIComponent(key)}.json`);
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
      <div className="gk-text">
        {verse.words.map((w) => (
          <button
            key={w.i}
            className={`gk-word${sel === w.i ? " sel" : ""}`}
            onClick={() => selectWord(w)}
          >
            <span className="gk-surface">{w.word}</span>
            <span className="gk-gloss">{w.gloss ?? "—"}</span>
            <span className="gk-morph">{w.morph}</span>
          </button>
        ))}
      </div>

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
