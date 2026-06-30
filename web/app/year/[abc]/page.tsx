import Link from "next/link";
import { notFound } from "next/navigation";
import { indexByYear, seasonRank, YEARS, type IndexEntry } from "@/lib/data";

export function generateStaticParams() {
  return YEARS.map((y) => ({ abc: y.toLowerCase() }));
}

export const dynamicParams = false;

const YEAR_LEDE: Record<string, string> = {
  A: "Matthew's Gospel · the Sermon on the Mount, the parables of the kingdom.",
  B: "Mark's Gospel (with John's bread of life) · the way of the cross.",
  C: "Luke's Gospel · the great reversal, the road to Jerusalem.",
};

function groupOrdered(items: IndexEntry[]): { season: string; items: IndexEntry[] }[] {
  const groups = new Map<string, IndexEntry[]>();
  for (const e of items) {
    const s = e.season || "Other";
    if (!groups.has(s)) groups.set(s, []);
    groups.get(s)!.push(e);
  }
  // Preserve the index's liturgical order across seasons via seasonRank.
  return [...groups.entries()]
    .sort((a, b) => seasonRank(a[0]) - seasonRank(b[0]))
    .map(([season, its]) => ({ season, items: its }));
}

export default async function YearPage({ params }: { params: Promise<{ abc: string }> }) {
  const { abc } = await params;
  const year = abc.toUpperCase();
  if (!YEARS.includes(year as (typeof YEARS)[number])) notFound();
  const items = indexByYear(year);
  if (!items.length) notFound();
  const blocks = groupOrdered(items);

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
            <Link
              key={y}
              className={"btn" + (y === year ? "" : " ghost")}
              href={`/year/${y.toLowerCase()}/`}
            >
              Year {y}
            </Link>
          ))}
          <Link className="btn ghost" href={`/series/${year.toLowerCase()}/`}>
            as series ↗
          </Link>
        </div>
      </header>

      <div className="yearhead">
        <h1>Year {year}</h1>
        <div className="sub">{YEAR_LEDE[year]} — {items.length} occasions across the church year.</div>
      </div>

      {blocks.map(({ season, items }) => (
        <section className="season-block" key={season}>
          <span className="eyebrow">{season}</span>
          <div className="occ-grid">
            {items.map((e) => {
              const gospel = e.readings.find((r) => r.role === "gospel");
              return (
                <Link className="occ-card" href={`/${e.id}/`} key={e.id}>
                  <div className="nm">{e.name}</div>
                  {gospel ? <div className="rd">{gospel.ref}</div> : null}
                  <div className="tk">
                    {e.trackKeys.length > 1 ? "dual track" : "single track"}
                    {e.hasCalls ? " · call ready" : ""}
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
      ))}

      <div className="footer">
        The lectionary is a deck of series waiting to be dealt. Browse a Sunday to open its
        workbench.
      </div>
    </div>
  );
}
