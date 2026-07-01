"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import type { BookMeta } from "@/lib/greek";

export default function GreekJump({ books }: { books: BookMeta[] }) {
  const router = useRouter();
  const [book, setBook] = useState(books[0]?.code ?? "");
  const [chapter, setChapter] = useState("1");
  const [verse, setVerse] = useState("1");

  const meta = books.find((b) => b.code === book);
  const chapters = meta ? Object.keys(meta.chapters) : [];
  const maxVerse = meta ? meta.chapters[chapter] ?? 1 : 1;
  const verses = Array.from({ length: maxVerse }, (_, i) => String(i + 1));

  return (
    <form
      className="gk-jump"
      onSubmit={(e) => {
        e.preventDefault();
        router.push(`/greek/${book}.${chapter}.${verse}/`);
      }}
    >
      <select value={book} onChange={(e) => { setBook(e.target.value); setChapter("1"); setVerse("1"); }}>
        {books.map((b) => (
          <option key={b.code} value={b.code}>{b.name}</option>
        ))}
      </select>
      <select value={chapter} onChange={(e) => { setChapter(e.target.value); setVerse("1"); }}>
        {chapters.map((c) => (
          <option key={c} value={c}>{c}</option>
        ))}
      </select>
      <select value={verse} onChange={(e) => setVerse(e.target.value)}>
        {verses.map((v) => (
          <option key={v} value={v}>{v}</option>
        ))}
      </select>
      <button type="submit">Go</button>
    </form>
  );
}
