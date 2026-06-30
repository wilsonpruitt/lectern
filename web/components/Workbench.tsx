"use client";

import { useState } from "react";
import Link from "next/link";
import type { Occasion, Track, Lenses as LensesData } from "@/lib/data";

type TabKey = "sermons" | "hymns" | "calls" | "turn" | "lenses";

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

function Readings({ track }: { track: Track }) {
  return (
    <ul className="readings">
      {track.readings.map((r) => (
        <li className="reading" key={r.role + r.refKey}>
          <div className="role">{r.role}</div>
          <div className="ref">{r.ref}</div>
        </li>
      ))}
    </ul>
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
            <span className="title">{s.title}</span>
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
              <span className="title">{d.title}</span>
              <span className="doctrine-themes">{d.themes.join(" · ")}</span>
            </a>
          ))}
        </div>
      ) : null}

      <p className="lens-foot micro">
        Coming: Greek &amp; Hebrew reading helps. {!anyLinks ? "" : ""}
      </p>
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

export default function Workbench({
  occ,
  yearHref,
  prevId,
  nextId,
}: {
  occ: Occasion;
  yearHref: string;
  prevId: string | null;
  nextId: string | null;
}) {
  const trackKeys = Object.keys(occ.tracks);
  const dual = trackKeys.length > 1;
  const [track, setTrack] = useState(
    trackKeys.includes("complementary") ? "complementary" : trackKeys[0]
  );
  const [tab, setTab] = useState<TabKey>("sermons");
  const [reg, setReg] = useState("A");

  const t = occ.tracks[track] ?? occ.tracks[trackKeys[0]];
  const o = occ.occasion;

  const tabs: [TabKey, string, boolean][] = [
    ["sermons", "Sermons", false],
    ["hymns", "Hymns", false],
    ["calls", "Call to Worship", false],
    ["lenses", "Lenses", false],
    ["turn", "The Turn", true],
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
          <div className="meta">{o.season}</div>
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

      <div className="workbench">
        <aside className="rail">
          <span className="eyebrow">The day · {t.label} track</span>
          <Readings track={t} />
        </aside>
        <main className="panel">
          <div className="tabs">
            {tabs.map(([k, lbl, dis]) => (
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
          <div className="panel-body">
            {tab === "sermons" && <Sermons track={t} />}
            {tab === "hymns" && <Hymns track={t} />}
            {tab === "calls" && <Calls occ={occ} reg={reg} setReg={setReg} />}
            {tab === "lenses" && <Lenses lenses={t.lenses} />}
            {tab === "turn" && (
              <Soon
                title="The Turn"
                desc="Reduce the day's abundance to two or three attested focus drafts — one thing to say, one thing to do."
              />
            )}
          </div>
        </main>
      </div>
    </>
  );
}
