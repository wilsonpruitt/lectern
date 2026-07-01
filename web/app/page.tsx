import Link from "next/link";
import { indexByYear, YEARS } from "@/lib/data";
import { weeksAhead, CURRENT } from "@/lib/now";

const YEAR_LEDE: Record<string, string> = {
  A: "Matthew · the kingdom in parables",
  B: "Mark · the way of the cross",
  C: "Luke · the great reversal",
};

const TOOLS = [
  ["Readings", "The day's appointed texts, anchored — semicontinuous or complementary track."],
  ["Sermons", "Wesley sermons that resonate by meaning, connected through shared faceted tags."],
  ["Hymns", "UMH & Faith We Sing recommendations from the day's images — pointer-only."],
  ["Call to Worship", "Three registers per Sunday — spare, immersive, hybrid — woven from the readings."],
  ["Lenses", "How the church has read it: Catena, Topographia, Annales, and the day's doctrine."],
  ["The Turn", "Two or three attested focus drafts from the church's own readings — one thing to say."],
];

export default function Home() {
  const counts = Object.fromEntries(YEARS.map((y) => [y, indexByYear(y).length]));
  const ahead = weeksAhead(5);
  const [thisSunday, ...rest] = ahead;

  return (
    <div className="wrap">
      <section className="hero">
        <p className="lectern-xl">Lectern</p>
        <p className="thesis">
          You don&rsquo;t have to choose between the lectionary and a series — the
          lectionary is a deck of series waiting to be dealt. A workbench over the church
          year: the day&rsquo;s readings anchored, with sermon companions, hymns, calls to
          worship, the church&rsquo;s reading-traditions, and the Turn arranged around them.
        </p>
        <p className="imprint">
          a{" "}
          <a href="https://wrootpress.com" className="imprint-link">
            Wroot Press
          </a>{" "}
          workbench
        </p>
      </section>

      {thisSunday ? (
        <section className="this-sunday">
          <span className="eyebrow">This Sunday · Year {CURRENT.year}</span>
          <Link href={`/${thisSunday.id}/`} className="sunday-feature">
            <div className="sf-main">
              <div className="sf-name">
                {thisSunday.name}
                {thisSunday.display ? <span className="sf-date">{thisSunday.display}</span> : null}
              </div>
              <div className="sf-readings">
                {thisSunday.readings.map((r) => (
                  <span key={r.role} className="sf-reading">
                    <span className="role">{r.role}</span> {r.ref}
                  </span>
                ))}
              </div>
            </div>
            <div className="sf-badges">
              {thisSunday.hasTurn ? <span className="badge reed">The Turn ready</span> : null}
              {thisSunday.hasCalls ? <span className="badge">Call ready</span> : null}
              <span className="open">Open the workbench →</span>
            </div>
          </Link>

          {rest.length ? (
            <>
              <div className="ahead-label micro">The weeks ahead</div>
              <div className="ahead-grid">
                {rest.map((e) => {
                  const gospel = e.readings.find((r) => r.role === "gospel");
                  return (
                    <Link key={e.id} href={`/${e.id}/`} className="ahead-card">
                      <div className="ac-name">{e.name}</div>
                      {e.display ? <div className="ac-date">{e.display}</div> : null}
                      {gospel ? <div className="ac-gospel">{gospel.ref}</div> : null}
                      <div className="ac-badges">
                        {e.hasTurn ? <span className="dot reed" title="The Turn ready" /> : null}
                        {e.hasTurn ? "Turn" : <span className="ac-soon">Turn soon</span>}
                      </div>
                    </Link>
                  );
                })}
              </div>
            </>
          ) : null}
        </section>
      ) : null}

      <section className="tools">
        <span className="eyebrow">The workbench</span>
        <div className="tools-grid">
          {TOOLS.map(([name, desc]) => (
            <div className="tool" key={name}>
              <div className="tool-name">{name}</div>
              <div className="tool-desc">{desc}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="years">
        <span className="eyebrow">Browse the church year</span>
        <div className="yearpick">
          {YEARS.map((y) => (
            <div className="yearcard" key={y}>
              <Link href={`/year/${y.toLowerCase()}/`}>
                <div className="yr">Year {y}</div>
                <div className="lede">{YEAR_LEDE[y]}</div>
              </Link>
              <div className="count">
                <Link href={`/year/${y.toLowerCase()}/`}>{counts[y]} occasions</Link>
                {" · "}
                <Link href={`/series/${y.toLowerCase()}/`} className="yearcard-series">
                  as series →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="footer">
        <div className="footer-links">
          <a href="https://wrootpress.com">Wroot Press ↗</a>
          <span className="dot-sep">·</span>
          <a href="https://wrootlabs.com">Wroot Labs ↗</a>
        </div>
        Recommendations connect readings, sermons, and hymns by shared faceted tags — not
        scripture coincidence. The Turn&rsquo;s focus drafts are surfaced from the church&rsquo;s
        attested reading-traditions (Catena Aurea), not generated. Pointer-only: no
        copyrighted hymn, sermon, or confessional text is stored.
      </div>
    </div>
  );
}
