/* Commission Studio — front end.
   No framework: the page renders the agent's structured state directly. */

const $ = (id) => document.getElementById(id);
const eur = (n) =>
  typeof n === "number" ? "EUR " + n.toLocaleString("en-GB") : "unavailable";

/* The server owns conversation memory; the page only remembers which
   conversation it is looking at. */
const state = { conversationId: null, busy: false };

/* ---------- boot ---------- */

async function boot() {
  try {
    const data = await (await fetch("/api/bootstrap")).json();
    renderStatus(data.status);
    renderSamples(data.samples);
    renderMeter(data.usage);
    const c = data.catalogue;
    $("m-catalogue").textContent =
      `${c.paints} paints · ${c.leathers} leathers · ${c.options} options`;
    loadConversations();
  } catch (err) {
    setStatus(false, "server unreachable");
  }
}

function setStatus(live, text) {
  $("status-dot").className = "dot " + (live ? "live" : "down");
  $("status-text").textContent = text;
}

function renderStatus(status) {
  if (status.ready) setStatus(true, status.model);
  else setStatus(false, "model not connected");
}

function renderMeter(u) {
  if (!u) return;
  $("m-calls").textContent = u.calls;
  $("m-fail").textContent = u.failures;
  $("m-tokens").textContent = u.total_tokens.toLocaleString("en-GB");
}

function renderSamples(samples) {
  const host = $("samples");
  host.innerHTML = "";
  samples.forEach((s) => {
    const b = document.createElement("button");
    b.className = "sample";
    b.type = "button";
    b.innerHTML =
      `<div class="sample-title"></div>` +
      `<div class="sample-note"></div>` +
      `<div class="sample-arrow">Use this brief &rarr;</div>`;
    b.querySelector(".sample-title").textContent = s.title;
    b.querySelector(".sample-note").textContent = s.note;
    b.addEventListener("click", () => submit(s.brief));
    host.appendChild(b);
  });
}

/* ---------- submission ---------- */

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

  try {
    const res = await fetch("/api/brief", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ brief, conversation_id: state.conversationId }),
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();

    state.conversationId = data.conversation_id;
    $("new-conversation").hidden = false;
    loadConversations();

    appendDocument(data);
    renderMeter(data.usage);
    if (data.usage && data.usage.calls && data.usage.failures === data.usage.calls) {
      setStatus(false, "all model calls failed");
    }
  } catch (err) {
    appendError(err.message);
  } finally {
    state.busy = false;
    $("send").disabled = false;
    $("send").classList.remove("busy");
    $("brief").focus();
  }
}

function appendBrief(text) {
  const el = document.createElement("div");
  el.className = "turn-brief";
  el.textContent = text;
  $("thread").appendChild(el);
  el.scrollIntoView({ behavior: "smooth", block: "center" });
}

function appendError(message) {
  const el = document.createElement("div");
  el.className = "doc";
  el.innerHTML = `<div class="doc-foot"><p class="narrative"></p></div>`;
  el.querySelector(".narrative").textContent = "Could not reach the concierge: " + message;
  $("thread").appendChild(el);
}

/* ---------- the commission document ---------- */

function appendDocument(d) {
  const c = d.configuration;
  const p = d.price;
  const a = d.availability;
  const prov = d.provenance;

  const doc = document.createElement("article");
  doc.className = "doc";

  /* head */
  const head = document.createElement("div");
  head.className = "doc-head";
  head.innerHTML =
    `<div class="swatch"></div>` +
    `<div class="doc-title">` +
    `<h2 class="doc-model"></h2>` +
    `<div class="doc-finish"></div>` +
    `<div class="chips"></div>` +
    `</div>`;
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
  doc.appendChild(head);

  /* body: specification + ledger */
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
  tl.textContent = p.regional_factor && p.regional_factor !== 1
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

  /* foot: narrative, options, sources, notices */
  const foot = document.createElement("div");
  foot.className = "doc-foot";
  const narrative = document.createElement("p");
  narrative.className = "narrative";
  narrative.textContent = d.summary;
  foot.appendChild(narrative);

  if (prov.removed_for_budget && prov.removed_for_budget.length) {
    foot.appendChild(
      notice("Removed to meet the budget", prov.removed_for_budget.join(", ") +
        ". Raise these with the client — they were part of the brief.")
    );
  }
  if (prov.rejected && prov.rejected.length) {
    foot.appendChild(
      notice("Rejected — not in the catalogue", prov.rejected.join(", "))
    );
  }

  if (d.complementary && d.complementary.length) {
    const tags = document.createElement("div");
    tags.className = "tags";
    d.complementary.forEach((o) => tags.appendChild(tag(o)));
    foot.appendChild(tags);
  }
  if (d.knowledge && d.knowledge.length) {
    const tags = document.createElement("div");
    tags.className = "tags";
    d.knowledge.forEach((k) => tags.appendChild(tag(k.source)));
    foot.appendChild(tags);
  }
  doc.appendChild(foot);

  /* provenance */
  const strip = document.createElement("div");
  strip.className = "provenance";
  strip.appendChild(prov_item("brief read by", prov.brief));
  strip.appendChild(prov_item("configured by", prov.configuration));
  const proposals = document.createElement("span");
  proposals.className = "prov";
  proposals.innerHTML = `proposals <b class="rules"></b>`;
  proposals.querySelector("b").textContent = prov.proposals;
  strip.appendChild(proposals);
  doc.appendChild(strip);

  $("thread").appendChild(doc);
  doc.scrollIntoView({ behavior: "smooth", block: "start" });
}

function chip(text, kind) {
  const el = document.createElement("span");
  el.className = "chip" + (kind ? " " + kind : "");
  el.textContent = text;
  return el;
}

function tag(text) {
  const el = document.createElement("span");
  el.className = "tag";
  el.textContent = text;
  return el;
}

function notice(title, body) {
  const el = document.createElement("div");
  el.className = "notice";
  const strong = document.createElement("strong");
  strong.textContent = title + ": ";
  el.appendChild(strong);
  el.appendChild(document.createTextNode(body));
  return el;
}

function prov_item(label, value) {
  const el = document.createElement("span");
  el.className = "prov";
  el.appendChild(document.createTextNode(label + " "));
  const b = document.createElement("b");
  b.className = value === "llm" ? "llm" : "rules";
  b.textContent = value === "llm" ? "the model" : "rules";
  el.appendChild(b);
  return el;
}

/* ---------- history ---------- */

async function loadConversations() {
  try {
    const data = await (await fetch("/api/conversations")).json();
    renderConversations(data.conversations || []);
  } catch (err) {
    /* the drawer is a convenience; a failure here must not break the studio */
  }
}

function renderConversations(rows) {
  const host = $("drawer-list");
  host.innerHTML = "";
  if (!rows.length) {
    const empty = document.createElement("div");
    empty.className = "drawer-empty";
    empty.textContent = "No commissions yet. Configure one and it is kept here.";
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

    const del = document.createElement("button");
    del.className = "convo-del";
    del.type = "button";
    del.textContent = "×";
    del.setAttribute("aria-label", "Delete commission");
    del.addEventListener("click", async (e) => {
      e.stopPropagation();
      await fetch("/api/conversations/" + row.id, { method: "DELETE" });
      if (state.conversationId === row.id) startNew();
      loadConversations();
    });
    item.appendChild(del);
    host.appendChild(item);
  });
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

async function openConversation(id) {
  const res = await fetch("/api/conversations/" + id);
  if (!res.ok) return;
  const data = await res.json();

  state.conversationId = id;
  $("stage").hidden = true;
  $("thread").hidden = false;
  $("thread").innerHTML = "";
  $("new-conversation").hidden = false;

  data.messages.forEach((m) => {
    if (m.role === "user") appendBrief(m.content);
    else if (m.result) appendDocument(m.result);
  });
  closeDrawer();
  loadConversations();
}

function startNew() {
  state.conversationId = null;
  $("thread").innerHTML = "";
  $("thread").hidden = true;
  $("stage").hidden = false;
  $("new-conversation").hidden = true;
  closeDrawer();
  loadConversations();
  $("brief").focus();
}

function openDrawer() {
  loadConversations();
  $("drawer").hidden = false;
  $("scrim").hidden = false;
}
function closeDrawer() {
  $("drawer").hidden = true;
  $("scrim").hidden = true;
}

$("history-toggle").addEventListener("click", openDrawer);
$("drawer-close").addEventListener("click", closeDrawer);
$("scrim").addEventListener("click", closeDrawer);
$("new-conversation").addEventListener("click", startNew);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeDrawer();
});

/* ---------- composer ---------- */

function autosize() {
  const ta = $("brief");
  ta.style.height = "auto";
  ta.style.height = Math.min(ta.scrollHeight, 190) + "px";
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

boot();
