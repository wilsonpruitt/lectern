import { notFound } from "next/navigation";
import Workbench from "@/components/Workbench";
import { allOccasions, getOccasion, neighbors, indexEntry } from "@/lib/data";
import { greekIndex } from "@/lib/greek";

export function generateStaticParams() {
  return allOccasions().map((o) => ({ occasion: o.occasion.id }));
}

export const dynamicParams = false;

export default async function OccasionPage({
  params,
}: {
  params: Promise<{ occasion: string }>;
}) {
  const { occasion } = await params;
  const occ = getOccasion(occasion);
  if (!occ) notFound();
  const { prev, next } = neighbors(occasion);
  const series = indexEntry(occasion)?.series ?? [];
  const greekBooks = greekIndex().books.map((b) => b.code);
  return (
    <div className="wrap">
      <Workbench
        occ={occ}
        yearHref={`/year/${occ.occasion.year.toLowerCase()}/`}
        prevId={prev}
        nextId={next}
        series={series}
        greekBooks={greekBooks}
      />
      <div className="footer">
        Lectern · a Wroot Press workbench. Sermon &amp; hymn recommendations connect by
        shared faceted tags; calls to worship are AI-drafted and curated. Pointer-only —
        no copyrighted hymn or sermon text is stored.
      </div>
    </div>
  );
}
