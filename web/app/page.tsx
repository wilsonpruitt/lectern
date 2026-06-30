import Link from "next/link";
import { indexByYear, YEARS } from "@/lib/data";

const YEAR_LEDE: Record<string, string> = {
  A: "Matthew · the kingdom in parables",
  B: "Mark · the way of the cross",
  C: "Luke · the great reversal",
};

export default function Home() {
  const counts = Object.fromEntries(YEARS.map((y) => [y, indexByYear(y).length]));
  return (
    <div className="wrap">
      <section className="hero">
        <p className="lectern-xl">Lectern</p>
        <p className="thesis">
          You don&rsquo;t have to choose between the lectionary and a series — the
          lectionary is a deck of series waiting to be dealt. A workbench over the church
          year: the day&rsquo;s readings anchored, with Wesley sermon companions, hymn
          recommendations, and calls to worship arranged around them.
        </p>
        <p className="imprint">a Wroot Press workbench</p>
      </section>

      <div className="yearpick">
        {YEARS.map((y) => (
          <Link className="yearcard" href={`/year/${y.toLowerCase()}/`} key={y}>
            <div className="yr">Year {y}</div>
            <div className="lede">{YEAR_LEDE[y]}</div>
            <div className="count">{counts[y]} occasions →</div>
          </Link>
        ))}
      </div>

      <div className="footer">
        Recommendations connect readings, sermons, and hymns by shared faceted tags — not
        scripture coincidence. Pointer-only: no copyrighted hymn or sermon text is stored.
      </div>
    </div>
  );
}
