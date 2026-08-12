"use client";

// The This-Sunday strip, picked in the browser.
//
// Lectern is a static export, so anything that reads `new Date()` on the server
// freezes at build time — the landing kept announcing whatever Sunday was next
// when we last deployed. The whole dated year ships as a prop and the window is
// chosen at render, so a stale build still lands on the right week. The server
// pass renders the build-time pick, which hydration corrects if the deploy has
// aged past it.

import { useEffect, useState } from "react";
import Link from "next/link";
import type { IndexEntry } from "@/lib/data";
import { CURRENT, pickAhead } from "@/lib/now";

export default function ThisSunday({
  dated,
  buildDate,
  count = 5,
}: {
  dated: IndexEntry[];
  /** The date the site was built — the initial render, so hydration matches. */
  buildDate: string;
  count?: number;
}) {
  const [today, setToday] = useState(buildDate);
  useEffect(() => {
    // Local calendar date, not UTC — a Saturday-evening visitor in Austin should
    // still see tomorrow as This Sunday.
    const d = new Date();
    const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
    setToday(local.toISOString().slice(0, 10));
  }, []);

  const ahead = pickAhead(dated, count, today);
  const [thisSunday, ...rest] = ahead;
  if (!thisSunday) return null;

  return (
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
  );
}
