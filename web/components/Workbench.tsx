"use client";

import { useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import type {
  Occasion,
  Track,
  Lenses as LensesData,
  CatenaEchoes,
  Chronology,
  PlacesMapData,
  SeriesMembership,
  Turn as TurnData,
  TurnDoor,
} from "@/lib/data";

// Leaflet touches window/document directly -- load client-only, never in the SSG pass.
const PlacesMap = dynamic(() => import("./PlacesMap"), { ssr: false });

type TabKey = "notes" | "glossa" | "hymns" | "praise" | "calls" | "turn" | "lenses";

// canonical tradition key -> display label (mirrors src/turn_sources.py). New
// traditions (eastern/modern/reformation…) slot in here as sources are added.
const TRADITION_LABEL: Record<string, string> = {
  "latin-patristic": "Latin Fathers",
  "greek-patristic": "Greek Fathers",
  pseudonymous: "Greek Fathers (attrib.)",
  medieval: "Medieval",
  conciliar: "Conciliar",
  jewish: "Jewish",
  wesleyan: "Wesleyan",
  reformed: "Reformed",
  reformation: "Reformation",
  puritan: "Puritan",
  "protestant-19c": "19th-c. Protestant",
  eastern: "Eastern / Philokalic",
  modern: "Modern",
  intertext: "Scripture echo",
};

function Chips({ tags }: { tags: string[] }) {
  if (!tags?.length) return null;
  return (
    <div className="chips">
      {tags.map((t) => (
        <span className="chip" key={t}>
          {t}
        </span>
      ))}
    </div>
  );
}

// Link an NT reading to its Greek study page — the first verse of the pericope, and only for
// books we've baked Greek data for (avoids dead links while the corpus grows book by book).
function greekHref(refKey: string, greekBooks: string[]): string | null {
  const start = refKey.split("-")[0];
  const [book, ch, v] = start.split(".");
  if (!v || !greekBooks.includes(book)) return null;
  return `/greek/${book}.${ch}.${v}/`;
}

function Readings({ track, greekBooks }: { track: Track; greekBooks: string[] }) {
  return (
    <ul className="readings">
      {track.readings.map((r) => {
        const gk = greekHref(r.refKey, greekBooks);
        return (
          <li className="reading" key={r.role + r.refKey}>
            <div className="role">{r.role}</div>
            <div className="ref">{r.ref}</div>
            {gk && (
              <Link className="study-greek" href={gk} target="_blank" rel="noopener noreferrer">
                Study the Greek ↗
              </Link>
            )}
          </li>
        );
      })}
    </ul>
  );
}

function Notes({ track }: { track: Track }) {
  const anyNotes = track.readings.some((r) => r.notes.length > 0);
  return (
    <div className="notes">
      <p className="lenses-intro">
        John Wesley&rsquo;s own <em>Explanatory Notes Upon the Old and New Testament</em> on
        the day&rsquo;s readings &mdash; his verse-by-verse commentary, not a summary of it.{" "}
        <a
          className="notes-source-link"
          href="https://notes.historyofmethodism.com"
          target="_blank"
          rel="noopener noreferrer"
        >
          Read the full edition ↗
        </a>
      </p>
      {!anyNotes ? (
        <div className="empty">Wesley did not comment on any of today&rsquo;s readings.</div>
      ) : (
        track.readings.map((r) => (
          <div className="notes-reading" key={r.role + r.refKey}>
            <div className="notes-reading-head">
              <span className="role">{r.role}</span> {r.ref}
            </div>
            {r.notes.length ? (
              <ul className="wesley-notes">
                {r.notes.map((n, i) => {
                  const vrange =
                    n.v_start === n.v_end ? `${n.v_start}` : `${n.v_start}–${n.v_end}`;
                  return (
                    <li className="wesley-note" key={i}>
                      <span className="wn-v">v.{vrange}</span>
                      <span className="wn-text">{n.text}</span>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <div className="empty small">no note on this passage</div>
            )}
          </div>
        ))
      )}

      <div className="related-sermons">
        <span className="eyebrow">Related Wesley sermons</span>
        <Sermons track={track} />
      </div>
    </div>
  );
}

// Renders the Glossa's lemma markup as <em> and \n\n-separated blocks as paragraphs --
// no markdown library, just enough to keep the lemma visually distinct from the comment.
// Some chunks mark the lemma with *asterisks*, others with «guillemets» (an inconsistency
// across translation stints, not a data error); both render the same way here.
function glossMarkup(text: string, keyPrefix: string) {
  return text.split(/\n\n+/).map((para, pi) => (
    <p key={`${keyPrefix}-${pi}`}>
      {para
        .split(/(\*[^*]+\*|«[^»]+»)/g)
        .filter((s) => s !== "")
        .map((part, i) => {
          const asterisk = part.match(/^\*([^*]+)\*$/);
          const guillemet = part.match(/^«\s*([^»]+?)\s*»$/);
          if (asterisk) return <em key={i}>{asterisk[1]}</em>;
          if (guillemet) return <em key={i}>{guillemet[1]}</em>;
          return <span key={i}>{part}</span>;
        })}
    </p>
  ));
}

function Glossa({ track }: { track: Track }) {
  const anyGlossa = track.readings.some((r) => r.glossa.length > 0);
  return (
    <div className="notes">
      <p className="lenses-intro">
        The <em>Glossa ordinaria</em> on the day&rsquo;s readings &mdash; the standard medieval
        commentary a reader met in the margins of the Bible, here in Migne&rsquo;s abridged
        nineteenth-century recension: marginal gloss only, fifty-five of the Bible&rsquo;s books,
        misattributed on its title page to Walafrid Strabo though it is the work of a school.{" "}
        <a
          className="notes-source-link"
          href="https://patrologia.wrootpress.com/glossa/"
          target="_blank"
          rel="noopener noreferrer"
        >
          Read the full edition ↗
        </a>
      </p>
      {!anyGlossa ? (
        <div className="empty">The Glossa has no comment on any of today&rsquo;s readings.</div>
      ) : (
        track.readings.map((r) => (
          <div className="notes-reading" key={r.role + r.refKey}>
            <div className="notes-reading-head">
              <span className="role">{r.role}</span> {r.ref}
            </div>
            {r.glossa.length ? (
              <ul className="wesley-notes">
                {r.glossa.map((g, i) => {
                  const vrange =
                    g.v_start === g.v_end ? `${g.v_start}` : `${g.v_start}–${g.v_end}`;
                  return (
                    <li className="wesley-note glossa-note" key={i}>
                      <span className="wn-v">v.{vrange}</span>
                      <div className="wn-text">{glossMarkup(g.text, `${r.refKey}-${i}`)}</div>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <div className="empty small">
                {r.glossaBookCovered
                  ? "The Glossa has no comment on this passage"
                  : "Migne's recension does not include this book"}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

function Sermons({ track }: { track: Track }) {
  if (!track.sermons.length)
    return <div className="empty">No Wesley sermon shares the day&rsquo;s tags.</div>;
  return (
    <>
      {track.sermons.map((s, i) => (
        <div className="rec" key={i}>
          <div className="line1">
            {s.url ? (
              <a className="title link" href={s.url} target="_blank" rel="noopener noreferrer">
                {s.title} ↗
              </a>
            ) : (
              <span className="title">{s.title}</span>
            )}
            {s.author ? <span className="by">{s.author}</span> : null}
            <span className="score">{s.score.toFixed(1)}</span>
          </div>
          {s.text ? <div className="text">text: {s.text}</div> : null}
          <Chips tags={s.tags} />
        </div>
      ))}
    </>
  );
}

function Hymns({ track }: { track: Track }) {
  if (!track.hymns.length)
    return <div className="empty">No tagged hymn shares the day&rsquo;s tags.</div>;
  return (
    <>
      {track.hymns.map((h, i) => (
        <div className="rec" key={i}>
          <div className="line1">
            <span className="num">
              {h.hymnal} {h.number}
            </span>
            <span className="title">{h.title}</span>
            <span className="score">{h.score.toFixed(1)}</span>
          </div>
          <Chips tags={h.tags} />
        </div>
      ))}
    </>
  );
}

function Praise({ track }: { track: Track }) {
  if (!track.praise?.length)
    return <div className="empty">No praise song shares the day&rsquo;s tags yet.</div>;
  return (
    <>
      <p className="lenses-intro">
        From Covenant&rsquo;s own repertoire, connected by shared tags. Pointer-only —
        titles link out to find the song; usage is how often it&rsquo;s been sung.
      </p>
      {track.praise.map((s, i) => (
        <div className="rec" key={i}>
          <div className="line1">
            <a className="title link" href={s.url} target="_blank" rel="noopener noreferrer">
              {s.title} ↗
            </a>
            {s.frequency ? (
              <span className="by">
                {s.timesUsed}× · {s.frequency}
                {s.pd ? " · PD" : ""}
              </span>
            ) : null}
            <span className="score">{s.score.toFixed(1)}</span>
          </div>
          <Chips tags={s.tags} />
        </div>
      ))}
    </>
  );
}

function Calls({ occ, reg, setReg }: { occ: Occasion; reg: string; setReg: (k: string) => void }) {
  if (!occ.calls)
    return (
      <div className="empty">
        Call to worship not yet drafted for this day. (Drafts are AI-generated, then
        curated.)
      </div>
    );
  const registers = occ.calls.registers;
  const current = registers.find((r) => r.key === reg) ?? registers[0];
  return (
    <>
      <div className="reg-switch">
        {registers.map((r) => (
          <button key={r.key} aria-pressed={r.key === current.key} onClick={() => setReg(r.key)}>
            {r.key} · {r.label}
          </button>
        ))}
      </div>
      <div className="micro reg-desc">{current.desc}</div>
      {current.lines.map(([lead, resp], i) => (
        <p className="antiphon" key={i}>
          <span className="lead">{lead}</span>
          <span className="resp">{resp}</span>
        </p>
      ))}
    </>
  );
}

function Lenses({ lenses }: { lenses: LensesData }) {
  const anyLinks = lenses.readings.some((r) => r.links.length > 0);
  return (
    <div className="lenses">
      <p className="lenses-intro">
        Tools for interpretation across the Wroot Press family — how the text has been
        read, where and when it happened, what it means for belief. Not the text itself.
      </p>
      <ul className="lens-readings">
        {lenses.readings.map((r) => (
          <li key={r.role + r.refKey} className="lens-reading">
            <div className="lens-ref">
              <span className="role">{r.role}</span> {r.ref}
            </div>
            {r.links.length ? (
              <div className="lens-links">
                {r.links.map((l) => (
                  <a
                    key={l.resource + l.url}
                    className={`lens-link kind-${l.kind}`}
                    href={l.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <span className="lens-res">{l.resource}</span>
                    <span className="lens-lbl">{l.label}</span>
                  </a>
                ))}
              </div>
            ) : (
              <div className="lens-none">no resource covers this reading yet</div>
            )}
            {r.map && <PlacesMapPanel map={r.map} />}
            {r.chronology && <ChronologyPanel chronology={r.chronology} />}
            {r.echoes && <EchoesPanel echoes={r.echoes} />}
          </li>
        ))}
      </ul>

      {lenses.doctrine.length ? (
        <div className="doctrine">
          <span className="eyebrow">Theological application</span>
          <p className="micro reg-desc">
            What the church confesses on the day&rsquo;s themes — from Doctrine.
          </p>
          {lenses.doctrine.map((d) => (
            <a
              key={d.url}
              className="doctrine-link"
              href={d.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <span className="title">
                {d.title} <span className="article">· {d.article} ↗</span>
              </span>
              <span className="doctrine-themes">{d.themes.join(" · ")}</span>
            </a>
          ))}
        </div>
      ) : null}

      {lenses.social?.length ? (
        <div className="doctrine social-principles">
          <span className="eyebrow">Social-ethical application</span>
          <p className="micro reg-desc">
            What the church calls us to do — the UMC Social Principles, linked to the
            specific position at umc.org.
          </p>
          {lenses.social.map((s) => (
            <a
              key={s.url}
              className="doctrine-link"
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <span className="title">
                {s.community} <span className="article">· {s.topic} ↗</span>
              </span>
              <span className="doctrine-themes">{s.themes.join(" · ")}</span>
            </a>
          ))}
        </div>
      ) : null}

      <p className="lens-foot micro">
        Greek reading helps are live &mdash; tap &ldquo;Study the Greek&rdquo; on any New Testament
        reading to open the parsing and classical lexicon. Hebrew to follow.
      </p>
    </div>
  );
}

function EchoesPanel({ echoes }: { echoes: CatenaEchoes }) {
  return (
    <div className="inline-panel echoes-panel">
      <span className="eyebrow">Fathers &amp; echoes &mdash; Catena</span>
      {echoes.kind === "nt" ? (
        echoes.pericopes.map((per) => (
          <div className="echo-group" key={per.pericopeId}>
            {echoes.pericopes.length > 1 && <div className="echo-group-ref">{per.ref}</div>}
            {per.echoes.map((e, i) => (
              <div className="echo" key={i}>
                <div className="echo-head">
                  <span className={`echo-type type-${e.type}`}>{e.type}</span>
                  <span className="echo-source">{e.source}</span>
                  <span className={`echo-confidence conf-${e.confidence}`}>{e.confidence}</span>
                </div>
                <p className="echo-text">&ldquo;{e.text}&rdquo;</p>
                <p className="echo-note">{e.note}</p>
              </div>
            ))}
          </div>
        ))
      ) : (
        echoes.sources.map((src) => (
          <div className="echo-group" key={src.source}>
            <div className="echo-group-ref">{src.source} &mdash; later echoed in:</div>
            <div className="echo-occurrences">
              {src.occurrences.map((o) => (
                <a
                  key={o.refKey}
                  className={`occ-link conf-${o.confidence}`}
                  href={o.url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {o.refDisplay} <span className="occ-type">{o.type}</span>
                </a>
              ))}
            </div>
          </div>
        ))
      )}
      <p className="micro panel-attribution">{echoes.attribution}</p>
    </div>
  );
}

function ChronologyPanel({ chronology }: { chronology: Chronology }) {
  return (
    <div className="inline-panel chronology-panel">
      <span className="eyebrow">Where this sits &mdash; Annales</span>
      {chronology.editions.map((ed) => (
        <div className="chron-edition" key={ed.edition}>
          <a className="chron-edition-name" href={ed.editionUrl} target="_blank" rel="noopener noreferrer">
            {ed.edition} ↗
          </a>
          {ed.spans?.map((s, i) => (
            <div className="chron-span" key={`s${i}`}>
              <span className="chron-label">{s.label}</span>
              <span className="chron-years">
                {s.start}
                {s.end && s.end !== s.start ? `–${s.end}` : ""}
                {s.length ? ` (${s.length})` : ""}
              </span>
              {s.note && <p className="chron-note">{s.note}</p>}
            </div>
          ))}
          {ed.events?.map((e, i) => (
            <div className="chron-span" key={`e${i}`}>
              <span className="chron-label">{e.label}</span>
              <span className="chron-years">
                {e.approx ? "c. " : ""}
                {e.year < 0 ? `${-e.year} B.C.` : `A.D. ${e.year}`}
              </span>
              {e.note && <p className="chron-note">{e.note}</p>}
            </div>
          ))}
          {ed.harmony?.map((h, i) => (
            <div className="chron-span" key={`h${i}`}>
              <span className="chron-label">{h.title}</span>
              <span className="chron-years">
                {Object.entries(h.refs)
                  .map(([g, ref]) => `${g[0].toUpperCase()}${g.slice(1)} ${ref}`)
                  .join(" · ")}
              </span>
              {h.note && <p className="chron-note">{h.note}</p>}
            </div>
          ))}
        </div>
      ))}
      <p className="micro panel-attribution">{chronology.note}</p>
    </div>
  );
}

function PlacesMapPanel({ map }: { map: PlacesMapData }) {
  return (
    <div className="inline-panel map-panel">
      <span className="eyebrow">Map &amp; places &mdash; Topographia</span>
      {map.approxChapter && (
        <p className="micro map-approx">
          This reading spans a chapter Topographia hasn&rsquo;t mapped yet &mdash; showing
          chapter {map.approxChapter} instead.
        </p>
      )}
      <PlacesMap data={map} />
      <ul className="map-place-list">
        {map.places.map((p) => (
          <li key={p.key} className={`map-place tier-${p.tier}`}>
            <span className="place-name">{p.name}</span>
            <span className="place-tier micro">{p.tier}</span>
            {p.id && <span className="place-id micro">{p.id}</span>}
          </li>
        ))}
      </ul>
      <a className="chron-edition-name" href={map.chapterUrl} target="_blank" rel="noopener noreferrer">
        Open this chapter in Topographia ↗
      </a>
    </div>
  );
}

function TurnSeriesBox({ series, year }: { series: SeriesMembership[]; year: string }) {
  const withArc = series.filter((m) => m.arc || m.beat);
  return (
    <div className="turn-series">
      <span className="eyebrow">In its series · which beat to hit</span>
      {withArc.length ? (
        withArc.map((m) => (
          <div className="ts-row" key={m.id}>
            <Link href={`/series/${year.toLowerCase()}/`} className="ts-series">
              {m.book} <span className="wk">{m.week}/{m.of}</span>
            </Link>
            {m.beat ? (
              <div className="ts-beat">
                <span className="ts-beat-label">{m.beat.label}</span>
                {m.beat.note ? <span className="ts-beat-note">{m.beat.note}</span> : null}
              </div>
            ) : null}
          </div>
        ))
      ) : series.length ? (
        <p className="micro ts-none">
          This Sunday runs in {series.map((m) => `${m.book} (${m.week}/${m.of})`).join(", ")}
          {" "}— narrative beats for these tracks are still being written.
        </p>
      ) : (
        <p className="micro ts-none">Not part of a native series this week.</p>
      )}
      <p className="micro ts-thematic">Thematic series (a coming layer) will add their beats here too.</p>
    </div>
  );
}

function Turn({
  turn,
  track,
  series,
  year,
}: {
  turn: TurnData;
  track: string;
  series: SeriesMembership[];
  year: string;
}) {
  if (!turn)
    return (
      <Soon
        title="The Turn"
        desc="Reduce the day's abundance to two or three attested focus drafts — one thing to say, one thing to do. Built from the church's actual reading-traditions (Catena Aurea), not generated. Coming, week by week."
      />
    );
  // per-track gravity/synthesis (v2, Phase 4a) -- "single" covers occasions with
  // no dual tracks; the Gospel doors below are shared across tracks either way.
  const tt = turn.tracks[track] ?? turn.tracks["single"];
  return (
    <div className="turn">
      <div className="turn-head">
        <span className="eyebrow">The Turn · {turn.pericope}</span>
        {turn.status === "draft" ? <span className="badge">draft</span> : null}
      </div>

      <TurnSeriesBox series={series} year={year} />

      <div className="turn-frame">
        {tt?.gravity ? (
          <p className="turn-block"><span className="turn-lbl">The day&rsquo;s gravity</span>{tt.gravity}</p>
        ) : (
          <p className="turn-block turn-not-yet">
            <span className="turn-lbl">The day&rsquo;s gravity</span>
            Not yet authored for this track{tt ? ` (from ${tt.firstReading.ref})` : ""}.
          </p>
        )}
        <p className="turn-block"><span className="turn-lbl">The trap</span>{turn.trap}</p>
        <p className="turn-block hinge"><span className="turn-lbl">The hinge</span>{turn.hinge}</p>
      </div>

      <p className="turn-doors-intro micro">{turn.subtract}</p>

      <TurnDoors doors={turn.doors} />

      {tt?.firstReading.doors.length ? (
        <div className="first-reading-doors">
          <span className="eyebrow">Doors on {tt.firstReading.ref}</span>
          <TurnDoors doors={tt.firstReading.doors} />
        </div>
      ) : null}

      {tt?.synthesis ? (
        <div className="synthesis">
          <div className="synthesis-head">
            <span className="eyebrow">Synthesis · bringing the texts together</span>
            <span className="badge">editorial</span>
          </div>
          <p className="micro syn-note">
            Less the church&rsquo;s traditions, more your context — how the day&rsquo;s
            readings converge, and the move toward these people this week. It names the
            one thing; it doesn&rsquo;t preach it for you.
          </p>
          <p className="syn-block"><span className="turn-lbl">How they converge</span>{tt.synthesis.convergence}</p>
          <p className="syn-block claim"><span className="turn-lbl">The one thing together</span>{tt.synthesis.claim}</p>
          <p className="syn-block"><span className="turn-lbl">Here, this week</span>{tt.synthesis.here}</p>
        </div>
      ) : null}

      <p className="turn-source micro">{turn.source}</p>
    </div>
  );
}

const MIGNE_WORK = "Glossa ordinaria (Migne)";

// One door list, used for the shared Gospel doors and for a track's first-reading
// doors. A Migne Glossa witness gets a "Migne" tag so it reads as distinct from the
// Catena Aurea's second-hand "Gloss." fragments, which share the author name.
function TurnDoors({ doors }: { doors: TurnDoor[] }) {
  return (
    <div className="doors">
      {doors.map((d, i) => (
        <div className="door" key={i}>
          <div className="door-head">
            <span className="door-n">{i + 1}</span>
            <span className="door-landing">{d.landing}</span>
          </div>
          <p className="door-claim">{d.claim}</p>
          <ul className="witnesses">
            {d.witnesses.map((w, j) => (
              <li key={j} className="witness">
                <span className="father">
                  {w.author}
                  <span className="tradition">{TRADITION_LABEL[w.tradition] ?? w.tradition}</span>
                  {w.work === MIGNE_WORK ? <span className="pointer-tag">Migne</span> : null}
                  {w.mode === "pointer" ? <span className="pointer-tag">cited</span> : null}
                </span>
                <span className="reading">
                  {w.reading}
                  {w.mode === "pointer" && w.cite ? (
                    <span className="witness-cite"> — {w.cite}</span>
                  ) : null}
                </span>
              </li>
            ))}
          </ul>
          <div className="say-do">
            <p><span className="sd-lbl">Say</span>{d.say}</p>
            <p><span className="sd-lbl">Do</span>{d.do}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function Soon({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="slot-soon">
      <span className="eyebrow">Coming</span>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
  );
}

function SeriesStrip({ series, year }: { series: SeriesMembership[]; year: string }) {
  if (!series.length) return null;
  return (
    <div className="series-strip">
      <span className="series-strip-lbl">Series</span>
      {series.map((m) => (
        <span className="series-tag" key={m.id}>
          {m.prev ? (
            <Link className="step" href={`/${m.prev}/`} aria-label="previous in series">
              ‹
            </Link>
          ) : (
            <span className="step off">‹</span>
          )}
          <Link className="series-tag-main" href={`/series/${year.toLowerCase()}/`}>
            {m.book} <span className="wk">{m.week}/{m.of}</span>
          </Link>
          {m.next ? (
            <Link className="step" href={`/${m.next}/`} aria-label="next in series">
              ›
            </Link>
          ) : (
            <span className="step off">›</span>
          )}
        </span>
      ))}
    </div>
  );
}

export default function Workbench({
  occ,
  yearHref,
  prevId,
  nextId,
  series = [],
  greekBooks = [],
}: {
  occ: Occasion;
  yearHref: string;
  prevId: string | null;
  nextId: string | null;
  series?: SeriesMembership[];
  greekBooks?: string[];
}) {
  const trackKeys = Object.keys(occ.tracks);
  const dual = trackKeys.length > 1;
  const [track, setTrack] = useState(
    trackKeys.includes("complementary") ? "complementary" : trackKeys[0]
  );
  const [tab, setTab] = useState<TabKey>("notes");
  const [reg, setReg] = useState("A");

  const t = occ.tracks[track] ?? occ.tracks[trackKeys[0]];
  const o = occ.occasion;

  // Lectern's job this phase is a product for preachers, not a personal workbench —
  // Covenant's own song list is a church-specific example, not a core feature. Off by
  // default; a future personal/church build sets NEXT_PUBLIC_CHURCH_LAYER=1.
  const churchLayer = process.env.NEXT_PUBLIC_CHURCH_LAYER === "1";

  // Two clusters: readings move from interpretation into what the service needs.
  // The Turn anchors the first cluster and is never disabled — an empty week still
  // renders (synthesis, or a "coming" panel), never a dead grey tab.
  const clusters: [string, [TabKey, string, boolean][]][] = [
    [
      "Interpret → Preach",
      [
        ["notes", "Wesley's Notes", false],
        ["glossa", "Glossa", false],
        ["lenses", "Lenses", false],
        ["turn", "The Turn", false],
      ],
    ],
    [
      "For the service",
      [
        ["hymns", "Hymns", false],
        ["calls", "Call to Worship", false],
        ...(churchLayer ? ([["praise", "Your church's songs (example)", false]] as [TabKey, string, boolean][]) : []),
      ],
    ],
  ];

  return (
    <>
      <header className="masthead">
        <Link href="/" className="brandlink">
          <span className="lectern">Lectern</span>
          <span className="imprint">a Wroot Press workbench</span>
        </Link>
        <div className="occ">
          <div className="name">
            {o.name} · Year {o.year}
          </div>
          <div className="meta">
            {o.display ? <span className="occ-date">{o.display}</span> : null}
            {o.display ? " · " : ""}
            {o.season}
          </div>
        </div>
        <div className="spacer" />
        {dual ? (
          <div className="track-toggle">
            <button aria-pressed={track === "semicontinuous"} onClick={() => setTrack("semicontinuous")}>
              Semicontinuous
            </button>
            <button aria-pressed={track === "complementary"} onClick={() => setTrack("complementary")}>
              Complementary
            </button>
          </div>
        ) : null}
        <div className="weeknav">
          {prevId ? (
            <Link className="btn" href={`/${prevId}/`}>
              ‹ week
            </Link>
          ) : (
            <span className="btn" aria-disabled style={{ opacity: 0.4 }}>
              ‹ week
            </span>
          )}
          {nextId ? (
            <Link className="btn" href={`/${nextId}/`}>
              week ›
            </Link>
          ) : (
            <span className="btn" aria-disabled style={{ opacity: 0.4 }}>
              week ›
            </span>
          )}
          <Link className="btn ghost" href={yearHref}>
            the year ↗
          </Link>
        </div>
      </header>

      <SeriesStrip series={series} year={o.year} />

      <div className="workbench">
        <aside className="rail">
          <span className="eyebrow">The day · {t.label} track</span>
          <Readings track={t} greekBooks={greekBooks} />
        </aside>
        <main className="panel">
          <div className="tab-clusters">
            {clusters.map(([label, clusterTabs]) => (
              <div className="tab-cluster" key={label}>
                <span className="tab-cluster-lbl">{label}</span>
                <div className="tabs">
                  {clusterTabs.map(([k, lbl, dis]) => (
                    <button
                      key={k}
                      aria-selected={tab === k}
                      disabled={dis}
                      onClick={() => !dis && setTab(k)}
                    >
                      {lbl}
                      {dis ? " ·" : ""}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="panel-body">
            {tab === "notes" && <Notes track={t} />}
            {tab === "glossa" && <Glossa track={t} />}
            {tab === "hymns" && <Hymns track={t} />}
            {tab === "praise" && <Praise track={t} />}
            {tab === "calls" && <Calls occ={occ} reg={reg} setReg={setReg} />}
            {tab === "lenses" && <Lenses lenses={t.lenses} />}
            {tab === "turn" && <Turn turn={occ.turn} track={track} series={series} year={o.year} />}
          </div>
        </main>
      </div>
    </>
  );
}
