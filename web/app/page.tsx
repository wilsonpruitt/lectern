import Link from "next/link";
import { indexByYear, YEARS } from "@/lib/data";
import { CURRENT } from "@/lib/now";
import ThisSunday from "@/components/ThisSunday";

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
  // The whole dated year goes to the client — it picks the week from the visitor's
  // own date, so the strip doesn't freeze at whatever Sunday we last deployed on.
  const dated = indexByYear(CURRENT.year).filter((e) => e.date);

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

      <ThisSunday dated={dated} buildDate={new Date().toISOString().slice(0, 10)} />

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
