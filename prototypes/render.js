/* Lectern prototype renderer — builds three layouts (rail / grid / board) from the
   same shared data, so the only variable under test is the SPATIAL MODEL. */
const L = (function () {
  const D = window.LECTERN;
  const state = { track: "complementary", reg: "A", tab: "sermons", layout: "rail" };
  const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

  const chips = (tags) => `<div class="chips">${tags.map((t) => `<span class="chip">${esc(t)}</span>`).join("")}</div>`;

  function readings(track) {
    const t = D.tracks[track];
    return `<ul class="readings">${t.readings.map((r) => `
      <li class="reading"><div class="role">${r.role}</div><div class="ref">${esc(r.ref)}</div></li>`).join("")}</ul>`;
  }
  const daynote = () => `<p class="daynote">${esc(D.occasion.note)}</p>`;

  function sermons(track, limit) {
    const list = D.tracks[track].sermons.slice(0, limit || 99);
    return list.map((s) => `
      <div class="rec">
        <div class="line1"><span class="title">${esc(s.title)}</span>
          <span class="by">${esc(s.author)}</span>
          ${s.note ? `<span class="badge">on the gospel</span>` : ""}</div>
        <div class="text">text: ${esc(s.text)}</div>
        ${chips(s.tags)}
      </div>`).join("");
  }
  function hymns(track, limit) {
    const list = D.tracks[track].hymns.slice(0, limit || 99);
    return list.map((h) => `
      <div class="rec">
        <div class="line1"><span class="num">${h.hymnal} ${h.number}</span>
          <span class="title">${esc(h.title)}</span></div>
        ${chips(h.tags)}
      </div>`).join("");
  }
  function calls() {
    const reg = D.calls.registers.find((r) => r.key === state.reg);
    const sw = D.calls.registers.map((r) =>
      `<button data-reg="${r.key}" aria-pressed="${r.key === state.reg}">${r.key} · ${r.label}</button>`).join("");
    const body = reg.lines.map(([lead, resp]) =>
      `<p class="antiphon"><span class="lead">${esc(lead)}</span><span class="resp">${esc(resp)}</span></p>`).join("");
    return `<div class="reg-switch">${sw}</div><div class="micro" style="margin-bottom:12px">${esc(reg.desc)}</div>${body}`;
  }
  const soon = (name, desc) => `
    <div class="slot-soon"><span class="eyebrow">Coming</span><h3>${name}</h3><p>${desc}</p></div>`;

  /* ---- shared chrome ---- */
  function masthead() {
    const o = D.occasion;
    return `<header class="masthead">
      <div class="brand"><span class="lectern">Lectern</span><span class="imprint">a Wroot Press workbench</span></div>
      <div class="occ"><div class="name">${o.name} · Year ${o.year}</div>
        <div class="meta">${o.season} · ${o.exampleDate}</div></div>
      <div class="spacer"></div>
      <div class="track-toggle">
        <button data-track="semicontinuous" aria-pressed="${state.track === "semicontinuous"}">Semicontinuous</button>
        <button data-track="complementary" aria-pressed="${state.track === "complementary"}">Complementary</button>
      </div>
      <div class="weeknav"><button class="btn">‹ week</button><button class="btn">week ›</button>
        <button class="btn ghost">the year ↗</button></div>
    </header>`;
  }
  const card = (eyebrow, title, sub, inner) => `
    <section class="toolcard"><span class="eyebrow">${eyebrow}</span><h3>${title}</h3>
      ${sub ? `<div class="sub">${sub}</div>` : ""}${inner}</section>`;

  /* ---- layouts ---- */
  function layoutRail() {
    const tabs = [
      ["sermons", "Sermons", false], ["hymns", "Hymns", false],
      ["calls", "Call to Worship", false], ["turn", "The Turn", true], ["lenses", "Lenses", true],
    ];
    const panel = {
      sermons: sermons(state.track),
      hymns: hymns(state.track),
      calls: calls(),
      turn: soon("The Turn", "Reduce the day's abundance to two or three attested focus drafts — one thing to say."),
      lenses: soon("Lenses", "Catena echoes, commentary, and reception for each reading."),
    }[state.tab];
    return `<div style="display:flex;gap:0;min-height:70vh">
      <aside style="width:320px;flex:none;padding:24px;border-right:1px solid var(--border);background:var(--bg-sunken)">
        <span class="eyebrow">The day · ${D.tracks[state.track].label} track</span>
        ${readings(state.track)}<div style="margin-top:20px">${daynote()}</div>
      </aside>
      <main style="flex:1;padding:0 32px 24px">
        <div class="tabs">${tabs.map(([k, lbl, dis]) =>
          `<button data-tab="${k}" aria-selected="${state.tab === k}" ${dis ? "disabled" : ""}>${lbl}${dis ? " ·" : ""}</button>`).join("")}</div>
        <div style="padding-top:20px;max-width:640px">${panel}</div>
      </main></div>`;
  }
  function layoutGrid() {
    const readCard = `<section class="toolcard" style="grid-column:1/-1">
      <span class="eyebrow">The readings · ${D.tracks[state.track].label} track</span>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 32px;align-items:start">
        <div>${readings(state.track)}</div><div style="padding-top:8px">${daynote()}</div></div></section>`;
    const tiles = [
      card("Companion", "Wesley sermons", "connected by shared tags", sermons(state.track, 3)),
      card("Music", "Hymns", "from the day's images", hymns(state.track, 3)),
      card("Liturgy", "Call to worship", "three registers", calls()),
      soon("The Turn", "Two or three attested focus drafts — one thing to say."),
      soon("Lenses", "Echoes, commentary, reception per reading."),
    ];
    return `<div style="padding:24px 32px"><div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
      ${readCard}${tiles.join("")}</div></div>`;
  }
  function layoutBoard() {
    const col = (eyebrow, title, inner, soonp) => `
      <div style="flex:0 0 300px;border-right:1px solid var(--border);padding:20px 18px;${soonp ? "opacity:.85" : ""}">
        <span class="eyebrow">${eyebrow}</span><h3 style="margin:2px 0 14px">${title}</h3>${inner}</div>`;
    return `<div style="display:flex;overflow-x:auto;min-height:72vh">
      ${col("The day · " + D.tracks[state.track].label, "Readings", readings(state.track) + `<div style="margin-top:16px">${daynote()}</div>`)}
      ${col("Companion", "Wesley sermons", sermons(state.track))}
      ${col("Music", "Hymns", hymns(state.track))}
      ${col("Liturgy", "Call to worship", calls())}
      ${col("Coming", "The Turn", `<p class="micro">Two or three attested focus drafts — one thing to say.</p>`, true)}
      ${col("Coming", "Lenses", `<p class="micro">Echoes, commentary, reception per reading.</p>`, true)}
    </div>`;
  }

  const layouts = { rail: layoutRail, grid: layoutGrid, board: layoutBoard };
  function footer() {
    const names = { rail: "Pinned readings + tool tabs", grid: "Dashboard card-grid", board: "Column board" };
    return `<div class="proto-note">Layout: <b>${names[state.layout]}</b> · real Proper 23-A data ·
      one of three spatial models under test. Same content, different arrangement.</div>`;
  }

  function render() {
    document.getElementById("app").innerHTML = masthead() + layouts[state.layout]() + footer();
    wire();
  }
  function wire() {
    document.querySelectorAll("[data-track]").forEach((b) =>
      b.onclick = () => { state.track = b.dataset.track; render(); });
    document.querySelectorAll("[data-tab]").forEach((b) =>
      b.onclick = () => { if (!b.disabled) { state.tab = b.dataset.tab; render(); } });
    document.querySelectorAll("[data-reg]").forEach((b) =>
      b.onclick = () => { state.reg = b.dataset.reg; render(); });
  }
  return { init(layout) { state.layout = layout; render(); } };
})();
