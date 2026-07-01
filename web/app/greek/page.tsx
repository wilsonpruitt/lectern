import Link from "next/link";
import { greekIndex } from "@/lib/greek";
import GreekJump from "@/components/GreekJump";
import "./greek.css";

export default function GreekLanding() {
  const { books } = greekIndex();
  return (
    <div className="wrap gk-wrap">
      <header className="gk-head">
        <h1 className="gk-ref">Greek</h1>
      </header>
      <p className="gk-lede">
        Word-by-word parsing of the Greek New Testament with classical definitions — the
        parsing you&apos;d get from an interlinear, joined to Liddell-Scott-Jones and Middle
        Liddell (classical lexica, not a Bible dictionary). Jump to any verse:
      </p>

      <GreekJump books={books} />

      <ul className="gk-booklist">
        {books.map((b) => (
          <li key={b.code}>
            <Link href={`/greek/${b.code}.1.1/`}>{b.name}</Link>{" "}
            <span className="gk-quiet">
              {Object.keys(b.chapters).length} ch · {b.verseCount} verses
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
