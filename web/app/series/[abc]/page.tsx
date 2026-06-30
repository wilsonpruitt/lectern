import Link from "next/link";
import { notFound } from "next/navigation";
import { seriesByYear, orderedIndex, YEARS, type Series } from "@/lib/data";

export function generateStaticParams() {
  return YEARS.map((y) => ({ abc: y.toLowerCase() }));
}
export const dynamicParams = false;

const ROLE_ORDER = ["gospel", "first", "second"];
const ROLE_HEAD: Record<string, string> = {
  gospel: "Gospel tracks",
  first: "First-reading tracks (the Old Testament lectio continua)",
  second: "Epistle tracks",
};

export default async function SeriesPage({ params }: { params: Promise<{ abc: string }> }) {
  const { abc } = await params;
  const year = abc.toUpperCase();
  if (!YEARS.includes(year as (typeof YEARS)[number])) notFound();

  const names = new Map(orderedIndex().map((e) => [e.id, e.name]));
  const all = seriesByYear(year);
  const byRole: Record<string, Series[]> = {};
  for (const s of all) (byRole[s.role] ??= []).push(s);

  return (
    <div className="wrap">
      <header className="masthead">
        <Link href="/" className="brandlink">
          <span className="lectern">Lectern</span>
          <span className="imprint">a Wroot Press workbench</span>
        </Link>
        <div className="spacer" />
        <div className="weeknav">
          {YEARS.map((y) => (
            <Link key={y} className={"btn" + (y === year ? "" : " ghost")} href={`/series/${y.toLowerCase()}/`}>
              Year {y}
            </Link>
          ))}
          <Link className="btn ghost" href={`/year/${year.toLowerCase()}/`}>
            calendar ↗
          </Link>
        </div>
      </header>

      <div className="yearhead">
        <h1>Year {year} — the deck of series</h1>
        <div className="sub">
          The lectionary is a deck of series waiting to be dealt. These are the{" "}
          <em>native</em> series — the runs the RCL already reads week by week. Preach
          a track as it stands, or let it seed a series.
        </div>
      </div>

      {ROLE_ORDER.filter((r) => byRole[r]?.length).map((role) => (
        <section className="season-block" key={role}>
          <span className="eyebrow">{ROLE_HEAD[role]}</span>
          <div className="series-list">
            {byRole[role]
              .slice()
              .sort((a, b) => b.weeks - a.weeks)
              .map((s) => (
                <div className="series-card" key={s.id}>
                  <div className="series-head">
                    <span className="series-book">{s.book}</span>
                    <span className="series-weeks">{s.weeks} weeks</span>
                  </div>
                  <div className="series-span">
                    {s.from} → {s.to}
                  </div>
                  <div className="series-weeks-list">
                    {s.occasions.map((oid, i) => (
                      <Link key={oid} href={`/${oid}/`} className="series-week" title={names.get(oid) ?? oid}>
                        {i + 1}
                      </Link>
                    ))}
                  </div>
                </div>
              ))}
          </div>
        </section>
      ))}

      <div className="footer">
        Native series are computed from the lectionary itself — no editorial choices.
        Thematic re-cuts (non-contiguous Sundays gathered by theme) are a coming layer.
      </div>
    </div>
  );
}
