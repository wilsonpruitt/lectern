import Link from "next/link";
import { notFound } from "next/navigation";
import GreekVerse from "@/components/GreekVerse";
import { allRefKeys, getVerse, verseNeighbors } from "@/lib/greek";
import "../greek.css";

export function generateStaticParams() {
  return allRefKeys().map((ref) => ({ ref }));
}

export const dynamicParams = false;

export default async function GreekVersePage({
  params,
}: {
  params: Promise<{ ref: string }>;
}) {
  const { ref } = await params;
  const verse = getVerse(ref);
  if (!verse) notFound();
  const { prev, next } = verseNeighbors(ref);

  return (
    <div className="wrap gk-wrap">
      <header className="gk-head">
        <Link href="/" className="gk-brand">Lectern</Link>
        <Link href="/greek/" className="gk-back">
          ← Greek
        </Link>
        <h1 className="gk-ref">{verse.refDisplay}</h1>
        <nav className="gk-vnav">
          {prev ? <Link href={`/greek/${prev}/`}>‹ prev</Link> : <span className="off">‹ prev</span>}
          {next ? <Link href={`/greek/${next}/`}>next ›</Link> : <span className="off">next ›</span>}
        </nav>
      </header>

      <GreekVerse verse={verse} />

      <footer className="gk-foot">
        Parsing &amp; lemmas: <a href="https://github.com/morphgnt/sblgnt">MorphGNT</a> (SBLGNT,
        CC-BY-SA morphology; SBLGNT text under its EULA). Definitions: Perseus{" "}
        <a href="https://github.com/PerseusDL/lexica">LSJ</a> and Middle Liddell (CC-BY-SA) —
        classical lexica, not a Bible dictionary.
      </footer>
    </div>
  );
}
