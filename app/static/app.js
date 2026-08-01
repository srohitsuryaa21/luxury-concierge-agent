/* Commission Studio — front end.
   No framework: the page renders the agent's structured state directly. */

const $ = (id) => document.getElementById(id);
const eur = (n) => (typeof n === "number" ? "EUR " + n.toLocaleString("en-GB") : "unavailable");

/* The server owns conversation memory; the page only tracks what it is looking
   at. Sending history from the browser would let a client rewrite what the
   agent believes was said earlier in the sale. */
const state = {
  conversationId: null,
  busy: false,
  conversations: [],
  samples: [],
  filter: "",
  paletteIndex: 0,
  paletteItems: [],
};

const DAILY_TOKENS = 100000;

/* ── boot ─────────────────────────────────────────────────────── */

/* ── theme ────────────────────────────────────────────────────── */

/* Follow the operating system until the user states a preference, then honour
   that. Applied before the first paint by an inline script in the head to avoid
   a flash of the wrong theme. */
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  $("theme-icon").textContent = theme === "dark" ? "◐" : "◑";
  $("theme-toggle").title =
    theme === "dark" ? "Switch to light (Ctrl+J)" : "Switch to dark (Ctrl+J)";
}

function currentTheme() {
  return document.documentElement.getAttribute("data-theme") || "dark";
}

function toggleTheme() {
  const next = currentTheme() === "dark" ? "light" : "dark";
  localStorage.setItem("theme", next);
  applyTheme(next);
  toast(next === "dark" ? "Dark" : "Light");
}

function restoreTheme() {
  const saved = localStorage.getItem("theme");
  if (saved) return applyTheme(saved);
  const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
  applyTheme(prefersLight ? "light" : "dark");
}

window.matchMedia("(prefers-color-scheme: light)").addEventListener("change", (e) => {
  if (!localStorage.getItem("theme")) applyTheme(e.matches ? "light" : "dark");
});

async function boot() {
  restoreTheme();
  restoreSidebar();
  try {
    const data = await (await fetch("/api/bootstrap")).json();
    state.samples = data.samples || [];
    renderStatus(data.status);
    renderSamples(state.samples);
    renderMeter(data.usage, data.status);
    await loadConversations();
  } catch {
    setStatus(false, "server unreachable");
    toast("Could not reach the server", true);
  }
  $("brief").focus();
}

function setStatus(live, text) {
  $("status-dot").className = "dot " + (live ? "live" : "down");
  $("status-text").textContent = text;
}

function renderStatus(status) {
  if (status.ready) setStatus(true, status.model);
  else setStatus(false, "model not connected");
  $("m-model").textContent = status.model ? String(status.model).split("-")[0] : "—";
}

function renderMeter(u, status) {
  if (!u) return;
  $("m-calls").textContent = u.calls;
  const fail = $("m-fail");
  fail.textContent = u.failures;
  fail.className = u.failures ? "warn" : "";
  $("m-tokens").textContent = u.total_tokens.toLocaleString("en-GB");

  const pct = Math.min(100, (u.total_tokens / DAILY_TOKENS) * 100);
  const bar = $("m-bar");
  bar.style.width = pct + "%";
  bar.className = pct > 80 ? "hot" : "";

  if (u.calls && u.failures === u.calls) {
    setStatus(false, "all model calls failed");
    $("m-note").textContent = "answers are rule-based only";
  } else if (status && !status.ready) {
    $("m-note").textContent = "no API key configured";
  } else {
    $("m-note").textContent = "of 100,000 daily free tier";
  }
}

function renderSamples(samples) {
  const host = $("samples");
  host.innerHTML = "";
  samples.forEach((s) => {
    const b = document.createElement("button");
    b.className = "sample";
    b.type = "button";
    b.innerHTML =
      `<div class="sample-title"></div><div class="sample-note"></div>` +
      `<div class="sample-arrow">Use this brief &rarr;</div>`;
    b.querySelector(".sample-title").textContent = s.title;
    b.querySelector(".sample-note").textContent = s.note;
    b.addEventListener("click", () => submit(s.brief));
    host.appendChild(b);
  });
}

/* ── sidebar ──────────────────────────────────────────────────── */

const isNarrow = () => window.matchMedia("(max-width: 900px)").matches;

function restoreSidebar() {
  if (localStorage.getItem("sidebar") === "collapsed") {
    $("shell").classList.add("collapsed");
  }
}

function toggleSidebar() {
  const shell = $("shell");
  if (isNarrow()) {
    shell.classList.toggle("open-mobile");
    return;
  }
  shell.classList.toggle("collapsed");
  localStorage.setItem(
    "sidebar",
    shell.classList.contains("collapsed") ? "collapsed" : "open"
  );
}

$("collapse").addEventListener("click", toggleSidebar);
$("expand").addEventListener("click", toggleSidebar);

/* ── conversation list ────────────────────────────────────────── */

async function loadConversations() {
  try {
    const data = await (await fetch("/api/conversations")).json();
    state.conversations = data.conversations || [];
    renderConversations();
  } catch {
    /* the list is a convenience; a failure here must not break the studio */
  }
}

function renderConversations() {
  const host = $("convo-list");
  host.innerHTML = "";
  const q = state.filter.toLowerCase();
  const rows = q
    ? state.conversations.filter((r) => (r.title || "").toLowerCase().includes(q))
    : state.conversations;

  if (!rows.length) {
    const empty = document.createElement("div");
    empty.className = "list-empty";
    empty.textContent = state.filter
      ? "No commission matches that."
      : "No commissions yet. Configure one and it is kept here.";
    host.appendChild(empty);
    return;
  }

  rows.forEach((row) => {
    const item = document.createElement("button");
    item.className = "convo" + (row.id === state.conversationId ? " active" : "");
    item.type = "button";
    item.innerHTML = `<div class="convo-title"></div><div class="convo-meta"></div>`;
    item.querySelector(".convo-title").textContent = row.title;
    const meta = [
      row.turns + (row.turns === 1 ? " brief" : " briefs"),
      row.last_model,
      row.last_region,
      formatWhen(row.updated_at),
    ].filter(Boolean);
    item.querySelector(".convo-meta").textContent = meta.join(" · ");
    item.addEventListener("click", () => openConversation(row.id));

    const menu = document.createElement("div");
    menu.className = "convo-menu";

    const ren = document.createElement("button");
    ren.type = "button";
    ren.textContent = "✎";
    ren.title = "Rename";
    ren.addEventListener("click", (e) => {
      e.stopPropagation();
      startRename(item, row);
    });

    const del = document.createElement("button");
    del.type = "button";
    del.className = "del";
    del.textContent = "×";
    del.title = "Delete";
    del.addEventListener("click", async (e) => {
      e.stopPropagation();
      await fetch("/api/conversations/" + row.id, { method: "DELETE" });
      if (state.conversationId === row.id) startNew();
      toast("Commission deleted");
      loadConversations();
    });

    menu.append(ren, del);
    item.appendChild(menu);
    host.appendChild(item);
  });
}

function startRename(item, row) {
  const titleEl = item.querySelector(".convo-title");
  const input = document.createElement("input");
  input.className = "convo-rename";
  input.value = row.title;
  titleEl.replaceWith(input);
  input.focus();
  input.select();

  const commit = async () => {
    const title = input.value.trim();
    if (title && title !== row.title) {
      await fetch("/api/conversations/" + row.id, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title }),
      });
      toast("Renamed");
    }
    loadConversations();
  };
  input.addEventListener("blur", commit, { once: true });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); input.blur(); }
    if (e.key === "Escape") { input.value = row.title; input.blur(); }
    e.stopPropagation();
  });
  input.addEventListener("click", (e) => e.stopPropagation());
}

function formatWhen(iso) {
  if (!iso) return "";
  const then = new Date(iso);
  if (isNaN(then)) return "";
  const mins = Math.round((Date.now() - then.getTime()) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return mins + "m ago";
  if (mins < 1440) return Math.round(mins / 60) + "h ago";
  return then.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}

$("search").addEventListener("input", (e) => {
  state.filter = e.target.value;
  renderConversations();
});

async function openConversation(id) {
  const res = await fetch("/api/conversations/" + id);
  if (!res.ok) return;
  const data = await res.json();

  state.conversationId = id;
  $("stage").hidden = true;
  $("thread").hidden = false;
  $("thread").innerHTML = "";
  $("crumb-title").textContent = data.title;

  data.messages.forEach((m) => {
    if (m.role === "user") appendBrief(m.content);
    else if (m.result) appendDocument({ ...m.result, summary: m.content });
  });
  if (isNarrow()) $("shell").classList.remove("open-mobile");
  renderConversations();
}

function startNew() {
  state.conversationId = null;
  $("thread").innerHTML = "";
  $("thread").hidden = true;
  $("stage").hidden = false;
  $("crumb-title").textContent = "Commission Studio";
  if (isNarrow()) $("shell").classList.remove("open-mobile");
  renderConversations();
  $("brief").focus();
}

$("new-conversation").addEventListener("click", startNew);

/* ── submission, streamed ─────────────────────────────────────── */

async function submit(text) {
  const brief = (text || $("brief").value).trim();
  if (!brief || state.busy) return;

  state.busy = true;
  $("send").disabled = true;
  $("send").classList.add("busy");
  $("brief").value = "";
  autosize();

  $("stage").hidden = true;
  $("thread").hidden = false;
  appendBrief(brief);
  const skeleton = appendSkeleton();

  try {
    const res = await fetch("/api/brief/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ brief, conversation_id: state.conversationId }),
    });
    if (!res.ok || !res.body) throw new Error("HTTP " + res.status);
    await consume(res.body, skeleton);
  } catch (err) {
    skeleton.remove();
    appendError(err.message);
    toast("Could not configure the commission", true);
  } finally {
    state.busy = false;
    $("send").disabled = false;
    $("send").classList.remove("busy");
    $("brief").focus();
  }
}

/* Parse the SSE stream by hand: EventSource cannot POST, and the brief is too
   long to put in a query string. */
async function consume(body, skeleton) {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let narrative = null;
  let streamed = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let split;
    while ((split = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, split);
      buffer = buffer.slice(split + 2);

      const evLine = frame.split("\n").find((l) => l.startsWith("event:"));
      const dataLine = frame.split("\n").find((l) => l.startsWith("data:"));
      if (!evLine || !dataLine) continue;
      const event = evLine.slice(6).trim();
      let payload;
      try {
        payload = JSON.parse(dataLine.slice(5).trim());
      } catch {
        continue;
      }

      if (event === "document") {
        skeleton.remove();
        state.conversationId = payload.conversation_id;
        const doc = appendDocument(payload, { live: true });
        narrative = doc.querySelector(".narrative");
        narrative.textContent = "";
        narrative.classList.add("streaming");
        loadConversations();
      } else if (event === "token" && narrative) {
        streamed += payload.t;
        narrative.textContent = streamed;
      } else if (event === "warning") {
        toast(payload.message, true);
      } else if (event === "done") {
        if (narrative) narrative.classList.remove("streaming");
        if (narrative && !streamed.trim() && payload.summary) {
          narrative.textContent = payload.summary;
        }
        renderMeter(payload.usage);
        loadConversations();
      }
    }
  }
  if (narrative) narrative.classList.remove("streaming");
}

function appendBrief(text) {
  const el = document.createElement("div");
  el.className = "turn-brief";
  el.textContent = text;
  $("thread").appendChild(el);
  scrollToEnd();
  return el;
}

function appendSkeleton() {
  const el = document.createElement("div");
  el.className = "doc skeleton";
  el.innerHTML = `<div class="sk-line w40"></div><div class="sk-line w70"></div>
                  <div class="sk-line w55"></div><div class="sk-line w70"></div>`;
  $("thread").appendChild(el);
  scrollToEnd();
  return el;
}

function appendError(message) {
  const el = document.createElement("div");
  el.className = "doc";
  el.innerHTML = `<div class="doc-foot"><p class="narrative"></p></div>`;
  el.querySelector(".narrative").textContent = "Could not reach the concierge: " + message;
  $("thread").appendChild(el);
}

function scrollToEnd() {
  const s = $("scroll");
  s.scrollTop = s.scrollHeight;
}

/* ── the commission document ──────────────────────────────────── */

function appendDocument(d, opts = {}) {
  const c = d.configuration;
  const p = d.price;
  const a = d.availability;
  const prov = d.provenance || {};

  const doc = document.createElement("article");
  doc.className = "doc";

  const head = document.createElement("div");
  head.className = "doc-head";
  head.innerHTML =
    `<div class="swatch"></div>` +
    `<div class="doc-title"><h2 class="doc-model"></h2><div class="doc-finish"></div>` +
    `<div class="chips"></div></div>` +
    `<div class="doc-actions"></div>`;
  head.querySelector(".swatch").style.background = d.swatch;
  head.querySelector(".doc-model").textContent = c.model;
  head.querySelector(".doc-finish").textContent = c.exterior_finish;

  const chips = head.querySelector(".chips");
  chips.appendChild(chip(d.region, ""));
  if (p.budget_fit === "fits") chips.appendChild(chip("within budget", "good"));
  if (p.budget_fit === "over_budget") chips.appendChild(chip("over budget", "bad"));
  if (a.timeline_fit === "fits") chips.appendChild(chip("timeline fits", "good"));
  if (a.timeline_fit === "at risk") chips.appendChild(chip("timeline at risk", "warn"));
  chips.appendChild(chip(a.status + " · " + a.lead_time, ""));

  const actions = head.querySelector(".doc-actions");
  actions.appendChild(action("Copy", () => copyCommission(d)));
  actions.appendChild(action("Print", () => window.print()));
  doc.appendChild(head);

  const body = document.createElement("div");
  body.className = "doc-body";

  const spec = document.createElement("div");
  spec.className = "panel";
  spec.innerHTML = `<h3>Specification</h3><dl class="spec"></dl>`;
  const dl = spec.querySelector(".spec");
  [
    ["Exterior", c.exterior_finish],
    ["Cabin", c.interior_leather],
    ["Veneer", c.veneer],
    ["Wheel", c.wheel],
    ["Region", d.region],
    ["Lead time", a.lead_time],
  ].forEach(([k, v]) => {
    const dt = document.createElement("dt");
    dt.textContent = k;
    const dd = document.createElement("dd");
    dd.textContent = v;
    dl.append(dt, dd);
  });
  body.appendChild(spec);

  const ledger = document.createElement("div");
  ledger.className = "panel";
  ledger.innerHTML = `<h3>Estimate</h3><table class="ledger"><tbody></tbody></table>`;
  const tb = ledger.querySelector("tbody");
  (p.line_items || []).forEach((line) => {
    const tr = document.createElement("tr");
    if (line.category === "base") tr.className = "base";
    const td1 = document.createElement("td");
    td1.className = "item";
    td1.textContent = line.item;
    const td2 = document.createElement("td");
    td2.className = "amt";
    td2.textContent = line.price_eur ? line.price_eur.toLocaleString("en-GB") : "—";
    tr.append(td1, td2);
    tb.appendChild(tr);
  });
  const totalRow = document.createElement("tr");
  totalRow.className = "total";
  const tl = document.createElement("td");
  tl.textContent =
    p.regional_factor && p.regional_factor !== 1
      ? `Total · ${d.region} ×${p.regional_factor}`
      : "Total";
  const tr2 = document.createElement("td");
  tr2.className = "amt";
  tr2.textContent = eur(p.estimated_total);
  totalRow.append(tl, tr2);
  tb.appendChild(totalRow);

  const caveat = document.createElement("p");
  caveat.className = "caveat";
  caveat.textContent = p.confidence || "";
  ledger.appendChild(caveat);
  body.appendChild(ledger);
  doc.appendChild(body);

  const foot = document.createElement("div");
  foot.className = "doc-foot";
  const narrative = document.createElement("p");
  narrative.className = "narrative";
  narrative.textContent = d.summary || "";
  foot.appendChild(narrative);

  if (prov.removed_for_budget && prov.removed_for_budget.length) {
    foot.appendChild(
      notice(
        "Removed to meet the budget",
        prov.removed_for_budget.join(", ") +
          ". Raise these with the client — they were part of the brief."
      )
    );
  }
  if (prov.rejected && prov.rejected.length) {
    foot.appendChild(notice("Rejected — not in the catalogue", prov.rejected.join(", ")));
  }
  if (d.complementary && d.complementary.length) {
    const tags = document.createElement("div");
    tags.className = "tags";
    d.complementary.forEach((o) => tags.appendChild(tag(o, "")));
    foot.appendChild(tags);
  }
  if (d.knowledge && d.knowledge.length) {
    const tags = document.createElement("div");
    tags.className = "tags";
    d.knowledge.forEach((k) => tags.appendChild(tag(k.source, "knowledge")));
    foot.appendChild(tags);
  }
  doc.appendChild(foot);

  const strip = document.createElement("div");
  strip.className = "provenance";
  strip.appendChild(provItem("brief read by", prov.brief));
  strip.appendChild(provItem("configured by", prov.configuration));
  const proposals = document.createElement("span");
  proposals.className = "prov";
  proposals.innerHTML = `proposals <b class="rules"></b>`;
  proposals.querySelector("b").textContent = prov.proposals ?? "—";
  strip.appendChild(proposals);
  doc.appendChild(strip);

  $("thread").appendChild(doc);
  if (!opts.live) scrollToEnd();
  else doc.scrollIntoView({ behavior: "smooth", block: "start" });
  return doc;
}

function chip(text, kind) {
  const el = document.createElement("span");
  el.className = "chip" + (kind ? " " + kind : "");
  el.textContent = text;
  return el;
}
function tag(text, kind) {
  const el = document.createElement("span");
  el.className = "tag" + (kind ? " " + kind : "");
  el.textContent = text;
  return el;
}
function action(label, fn) {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = label;
  b.addEventListener("click", fn);
  return b;
}
function notice(title, body) {
  const el = document.createElement("div");
  el.className = "notice";
  const strong = document.createElement("strong");
  strong.textContent = title + ": ";
  el.append(strong, document.createTextNode(body));
  return el;
}
function provItem(label, value) {
  const el = document.createElement("span");
  el.className = "prov";
  el.appendChild(document.createTextNode(label + " "));
  const b = document.createElement("b");
  b.className = value === "llm" ? "llm" : "rules";
  b.textContent = value === "llm" ? "the model" : "rules";
  el.appendChild(b);
  return el;
}

async function copyCommission(d) {
  const c = d.configuration;
  const lines = [
    `${c.model} — ${c.exterior_finish}`,
    `Cabin: ${c.interior_leather}`,
    `Veneer: ${c.veneer}`,
    `Wheel: ${c.wheel}`,
    `Region: ${d.region} · ${d.availability.status}, ${d.availability.lead_time}`,
    "",
    ...(d.price.line_items || []).map(
      (l) => `  ${l.item} … ${l.price_eur ? l.price_eur.toLocaleString("en-GB") : "—"}`
    ),
    `  TOTAL … ${eur(d.price.estimated_total)}`,
    `  (${d.price.confidence})`,
    "",
    d.summary || "",
  ];
  try {
    await navigator.clipboard.writeText(lines.join("\n"));
    toast("Commission copied");
  } catch {
    toast("Clipboard unavailable", true);
  }
}

/* ── toasts ───────────────────────────────────────────────────── */

function toast(message, bad) {
  const el = document.createElement("div");
  el.className = "toast" + (bad ? " bad" : "");
  el.textContent = message;
  $("toasts").appendChild(el);
  setTimeout(() => el.remove(), 3600);
}

/* ── command palette ──────────────────────────────────────────── */

function paletteItems() {
  const items = [
    { kind: "Action", label: "New commission", run: startNew },
    { kind: "Action", label: "Toggle sidebar", run: toggleSidebar },
    { kind: "Action", label: "Print this page", run: () => window.print() },
  ];
  state.samples.forEach((s) =>
    items.push({ kind: "Brief", label: s.title + " — " + s.note, run: () => submit(s.brief) })
  );
  state.conversations.forEach((r) =>
    items.push({ kind: "Open", label: r.title, run: () => openConversation(r.id) })
  );
  return items;
}

function openPalette() {
  $("palette").hidden = false;
  $("palette-scrim").hidden = false;
  $("palette-input").value = "";
  filterPalette("");
  $("palette-input").focus();
}
function closePalette() {
  $("palette").hidden = true;
  $("palette-scrim").hidden = true;
}

function filterPalette(q) {
  const all = paletteItems();
  const query = q.toLowerCase();
  state.paletteItems = query
    ? all.filter((i) => i.label.toLowerCase().includes(query))
    : all;
  state.paletteIndex = 0;
  renderPalette();
}

function renderPalette() {
  const host = $("palette-results");
  host.innerHTML = "";
  if (!state.paletteItems.length) {
    const empty = document.createElement("div");
    empty.className = "palette-empty";
    empty.textContent = "Nothing matches.";
    host.appendChild(empty);
    return;
  }
  state.paletteItems.forEach((item, i) => {
    const b = document.createElement("button");
    b.className = "palette-item" + (i === state.paletteIndex ? " on" : "");
    b.type = "button";
    b.innerHTML = `<span class="palette-kind"></span><span class="palette-label"></span>`;
    b.querySelector(".palette-kind").textContent = item.kind;
    b.querySelector(".palette-label").textContent = item.label;
    b.addEventListener("click", () => { closePalette(); item.run(); });
    host.appendChild(b);
  });
}

$("palette-input").addEventListener("input", (e) => filterPalette(e.target.value));
$("palette-open").addEventListener("click", openPalette);
$("theme-toggle").addEventListener("click", toggleTheme);
$("palette-scrim").addEventListener("click", closePalette);
$("palette-input").addEventListener("keydown", (e) => {
  if (e.key === "ArrowDown") {
    e.preventDefault();
    state.paletteIndex = Math.min(state.paletteIndex + 1, state.paletteItems.length - 1);
    renderPalette();
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    state.paletteIndex = Math.max(state.paletteIndex - 1, 0);
    renderPalette();
  } else if (e.key === "Enter") {
    e.preventDefault();
    const item = state.paletteItems[state.paletteIndex];
    if (item) { closePalette(); item.run(); }
  }
});

/* ── composer + shortcuts ─────────────────────────────────────── */

function autosize() {
  const ta = $("brief");
  ta.style.height = "auto";
  ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
}

$("brief").addEventListener("input", autosize);
$("brief").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    submit();
  }
});
$("composer").addEventListener("submit", (e) => {
  e.preventDefault();
  submit();
});

document.addEventListener("keydown", (e) => {
  const meta = e.ctrlKey || e.metaKey;
  if (meta && e.key.toLowerCase() === "k") {
    e.preventDefault();
    $("palette").hidden ? openPalette() : closePalette();
  } else if (meta && e.key.toLowerCase() === "b") {
    e.preventDefault();
    toggleSidebar();
  } else if (meta && e.key.toLowerCase() === "j") {
    e.preventDefault();
    toggleTheme();
  } else if (meta && e.shiftKey && e.key.toLowerCase() === "n") {
    e.preventDefault();
    startNew();
  } else if (e.key === "Escape") {
    closePalette();
  }
});

boot();
