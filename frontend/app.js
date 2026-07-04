"use strict";

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------

async function api(path, opts) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `${res.status} ${res.statusText}`);
  }
  return res.json();
}

const get = (path) => api(path);
const post = (path, data) => api(path, { method: "POST", body: data ? JSON.stringify(data) : undefined });

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

const state = {
  briefing: null,
  board: null,
  currentSuspect: null,
  accusation: { culprit: null, motive: null, opportunity: null, means: null },
};

const TYPE_LABEL = {
  Victim: "Victim",
  Suspect: "Suspect",
  Location: "Location",
  Weapon: "Weapon",
  Motive: "Motive",
  TimelineEvent: "Timeline",
  Clue: "Clue",
  Statement: "Statement",
};

const TYPE_ORDER = ["Victim", "TimelineEvent", "Suspect", "Location", "Statement", "Clue", "Motive", "Weapon"];

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

async function boot() {
  document.getElementById("briefing-close").addEventListener("click", () => {
    document.getElementById("briefing-modal").classList.add("hidden");
  });
  document.getElementById("hint-btn").addEventListener("click", onHint);
  document.getElementById("new-game-btn").addEventListener("click", openCaseSelectModal);
  document.getElementById("how-to-play-btn").addEventListener("click", () => {
    document.getElementById("how-to-play-modal").classList.remove("hidden");
  });
  document.getElementById("accuse-btn").addEventListener("click", openAccusationModal);
  document.getElementById("submit-accusation").addEventListener("click", onSubmitAccusation);

  document.querySelectorAll("[data-close]").forEach((btn) => {
    btn.addEventListener("click", () => document.getElementById(btn.dataset.close).classList.add("hidden"));
  });

  window.addEventListener("resize", drawStrings);

  // First load (and every hard refresh) starts at the case picker, not a
  // pre-loaded case -- the server's default case is just a backend fallback.
  await openCaseSelectModal();
}

async function loadBriefingAndRender() {
  state.briefing = await get("/api/briefing");
  document.getElementById("case-name-text").textContent = `Case: ${state.briefing.title}`;
  document.title = `The Cognee Case Files -- ${state.briefing.title}`;
  document.getElementById("briefing-title").textContent = state.briefing.title;
  document.getElementById("briefing-summary").textContent = state.briefing.summary;

  renderLocations();
  renderSuspects();
  await refreshBoard();
}

// ---------------------------------------------------------------------------
// Case selection
// ---------------------------------------------------------------------------

async function openCaseSelectModal() {
  const { cases, active } = await get("/api/cases");
  const list = document.getElementById("case-list");
  list.innerHTML = "";
  for (const c of cases) {
    const card = document.createElement("button");
    card.className = "case-card" + (c.id === active ? " active" : "");
    card.innerHTML = `<span class="case-card-title">${c.title}</span><span class="case-card-blurb">${c.blurb}</span>`;
    card.addEventListener("click", () => selectCase(c.id));
    list.appendChild(card);
  }
  document.getElementById("case-select-modal").classList.remove("hidden");
}

async function selectCase(caseId) {
  document.getElementById("case-select-modal").classList.add("hidden");
  document.getElementById("interrogation-modal").classList.add("hidden");
  document.getElementById("accusation-modal").classList.add("hidden");
  document.getElementById("hint-modal").classList.add("hidden");
  document.getElementById("log-feed").innerHTML = "";
  try {
    await post("/api/new-game", { case_id: caseId });
    await loadBriefingAndRender();
    document.getElementById("briefing-modal").classList.remove("hidden");
  } catch (e) {
    log("Error: " + e.message, "log-error");
  }
}

// ---------------------------------------------------------------------------
// Log feed
// ---------------------------------------------------------------------------

function log(text, cls) {
  const feed = document.getElementById("log-feed");
  const line = document.createElement("p");
  line.className = "log-line" + (cls ? " " + cls : "");
  line.textContent = text;
  feed.prepend(line);
  while (feed.children.length > 12) feed.removeChild(feed.lastChild);
}

function toast(text) {
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = text;
  document.body.appendChild(t);
  requestAnimationFrame(() => t.classList.add("show"));
  setTimeout(() => {
    t.classList.remove("show");
    setTimeout(() => t.remove(), 400);
  }, 4200);
}

// ---------------------------------------------------------------------------
// Locations & suspects (left rail)
// ---------------------------------------------------------------------------

function renderLocations() {
  const wrap = document.getElementById("locations");
  wrap.innerHTML = "";
  for (const loc of state.briefing.locations) {
    const el = document.createElement("button");
    el.className = "rail-card location-card";
    el.innerHTML = `<span class="rail-card-name">${loc.name}</span>`;
    el.title = loc.description;
    el.addEventListener("click", () => onInvestigate(loc.slug));
    wrap.appendChild(el);
  }
}

function renderSuspects() {
  const wrap = document.getElementById("suspects");
  wrap.innerHTML = "";
  for (const s of state.briefing.suspects) {
    const el = document.createElement("button");
    el.className = "rail-card suspect-card";
    el.innerHTML = `<span class="rail-card-name">${s.name}</span><span class="rail-card-role">${s.role}</span>`;
    el.addEventListener("click", () => openInterrogationModal(s.slug));
    wrap.appendChild(el);
  }
}

// ---------------------------------------------------------------------------
// Investigate
// ---------------------------------------------------------------------------

async function onInvestigate(slug) {
  try {
    const result = await post(`/api/investigate/${slug}`);
    if (result.new_clues.length === 0) {
      log(`Nothing further of note in ${state.briefing.locations.find((l) => l.slug === slug).name}.`);
    } else {
      log(result.narration || `Found ${result.new_clues.length} clue(s).`, "log-discovery");
      for (const c of result.new_clues) toast(`Found: ${c.name}`);
    }
    await refreshBoard();
    announceContradictions(result.contradictions);
  } catch (e) {
    log("Error: " + e.message, "log-error");
  }
}

// ---------------------------------------------------------------------------
// Interrogate
// ---------------------------------------------------------------------------

async function openInterrogationModal(suspectSlug) {
  state.currentSuspect = suspectSlug;
  const s = state.briefing.suspects.find((x) => x.slug === suspectSlug);
  document.getElementById("interrogation-name").textContent = s.name;
  document.getElementById("interrogation-role").textContent = s.role;
  document.getElementById("interrogation-dialogue").innerHTML = '<p class="placeholder">Choose a question.</p>';
  document.getElementById("interrogation-contradiction").classList.add("hidden");

  const { topics } = await get(`/api/suspects/${suspectSlug}/topics`);
  const topicWrap = document.getElementById("interrogation-topics");
  topicWrap.innerHTML = "";
  for (const t of topics) {
    const btn = document.createElement("button");
    btn.className = "btn btn-topic";
    btn.textContent = t.label;
    btn.addEventListener("click", () => onInterrogate(suspectSlug, t.id));
    topicWrap.appendChild(btn);
  }

  document.getElementById("interrogation-modal").classList.remove("hidden");
}

async function onInterrogate(suspectSlug, topicId) {
  try {
    const result = await post("/api/interrogate", { suspect: suspectSlug, topic: topicId });
    const dialogue = document.getElementById("interrogation-dialogue");
    dialogue.innerHTML = `<p>${result.narration}</p>`;
    if (result.new_clues.length) {
      for (const c of result.new_clues) toast(`Found: ${c.name}`);
    }
    await refreshBoard();

    const mine = result.contradictions.filter((c) => c.speaker === suspectSlug);
    const box = document.getElementById("interrogation-contradiction");
    if (mine.length) {
      box.classList.remove("hidden");
      box.innerHTML = "";
      for (const c of mine) {
        const div = document.createElement("div");
        div.className = "contradiction-alert";
        div.innerHTML = `<strong>CONTRADICTION</strong><p>This claim doesn't square with "${c.clue_name}".</p>`;
        const btn = document.createElement("button");
        btn.className = "btn btn-accent";
        btn.textContent = "Confront";
        btn.addEventListener("click", () => onConfront(c.statement_slug, div));
        div.appendChild(btn);
        box.appendChild(div);
      }
    } else {
      box.classList.add("hidden");
    }
    announceContradictions(result.contradictions.filter((c) => c.speaker !== suspectSlug));
  } catch (e) {
    log("Error: " + e.message, "log-error");
  }
}

async function onConfront(statementSlug, containerEl) {
  try {
    const result = await post("/api/confront", { statement_slug: statementSlug });
    log(result.narration_hint, result.decoy ? "log-decoy" : "log-breakthrough");
    if (containerEl) {
      containerEl.classList.add("resolved");
      containerEl.innerHTML = `<strong>${result.decoy ? "A dead end." : "CONFRONTED"}</strong><p>${result.narration_hint}</p>`;
    }
    await refreshBoard();
  } catch (e) {
    log("Error: " + e.message, "log-error");
  }
}

function announceContradictions(list) {
  for (const c of list) {
    toast(`${nameFor(c.speaker)}'s story doesn't add up...`);
  }
}

function nameFor(slug) {
  const s = state.briefing.suspects.find((x) => x.slug === slug);
  return s ? s.name : slug;
}

// ---------------------------------------------------------------------------
// Hint
// ---------------------------------------------------------------------------

async function onHint() {
  try {
    const h = await get("/api/hint");
    document.getElementById("hint-text").textContent = h.text;
    document.getElementById("hint-modal").classList.remove("hidden");
    log("Hint: " + h.text, "log-hint");
  } catch (e) {
    log("Error: " + e.message, "log-error");
  }
}

// ---------------------------------------------------------------------------
// Board (evidence corkboard + red string)
// ---------------------------------------------------------------------------

async function refreshBoard() {
  state.board = await get("/api/board");
  renderBoard();
  updateContradictionBanner();
}

function updateContradictionBanner() {
  const banner = document.getElementById("contradiction-banner");
  const n = state.board.contradictions.length;
  if (n > 0) {
    banner.textContent = `${n} unresolved contradiction${n > 1 ? "s" : ""} on the board -- confront the liar.`;
    banner.classList.remove("hidden");
  } else {
    banner.classList.add("hidden");
  }
}

function renderBoard() {
  const canvas = document.getElementById("board-canvas");
  canvas.innerHTML = "";

  const byType = {};
  for (const n of state.board.nodes) {
    (byType[n.type] = byType[n.type] || []).push(n);
  }

  for (const type of TYPE_ORDER) {
    const nodes = byType[type];
    if (!nodes) continue;
    const col = document.createElement("div");
    col.className = "board-col";
    const label = document.createElement("div");
    label.className = "board-col-label";
    label.textContent = TYPE_LABEL[type] || type;
    col.appendChild(label);
    for (const n of nodes) {
      col.appendChild(renderCard(n));
    }
    canvas.appendChild(col);
  }

  requestAnimationFrame(drawStrings);
}

function renderCard(node) {
  const card = document.createElement("div");
  card.className = `board-card card-type-${node.type}`;
  card.id = `card-${node.slug}`;
  card.dataset.slug = node.slug;
  card.dataset.type = node.type;

  const title = document.createElement("div");
  title.className = "board-card-title";
  title.textContent = node.name || node.slug;
  card.appendChild(title);

  const bodyText = node.description || node.text || node.time || "";
  if (bodyText) {
    const body = document.createElement("div");
    body.className = "board-card-body";
    body.textContent = bodyText;
    card.appendChild(body);
  }
  if (node.role) {
    const role = document.createElement("div");
    role.className = "board-card-role";
    role.textContent = node.role;
    card.appendChild(role);
  }

  const isContradicted = state.board.contradictions.some(
    (c) => c.statement_slug === node.slug || c.clue_slug === node.slug
  );
  if (isContradicted) card.classList.add("contradicted");

  return card;
}

function drawStrings() {
  const svg = document.getElementById("string-layer");
  const canvas = document.getElementById("board-canvas");
  const scroll = document.getElementById("board-scroll");
  if (!state.board) return;

  const width = canvas.scrollWidth;
  const height = canvas.scrollHeight;
  svg.setAttribute("width", width);
  svg.setAttribute("height", height);
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.innerHTML = "";

  const canvasRect = canvas.getBoundingClientRect();

  const SKIP_RELATIONS = new Set(["found-at", "revealed-by"]);

  for (const edge of state.board.edges) {
    const a = document.getElementById(`card-${edge.source}`);
    const b = document.getElementById(`card-${edge.target}`);
    if (!a || !b) continue;

    const ra = a.getBoundingClientRect();
    const rb = b.getBoundingClientRect();
    const x1 = ra.left - canvasRect.left + ra.width / 2;
    const y1 = ra.top - canvasRect.top + ra.height / 2;
    const x2 = rb.left - canvasRect.left + rb.width / 2;
    const y2 = rb.top - canvasRect.top + rb.height / 2;

    const midX = (x1 + x2) / 2;
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", `M ${x1} ${y1} Q ${midX} ${(y1 + y2) / 2} ${x2} ${y2}`);
    const isContradiction = edge.relation === "contradicts";
    const isFaint = SKIP_RELATIONS.has(edge.relation);
    path.setAttribute("class", "string" + (isContradiction ? " string-contradiction" : "") + (isFaint ? " string-faint" : ""));
    svg.appendChild(path);
  }
}

// ---------------------------------------------------------------------------
// Accusation
// ---------------------------------------------------------------------------

function openAccusationModal() {
  state.accusation = { culprit: null, motive: null, opportunity: null, means: null };
  document.querySelectorAll("#accusation-modal .slot-drop").forEach((el) => (el.innerHTML = ""));
  document.getElementById("verdict-box").classList.add("hidden");
  document.getElementById("verdict-box").innerHTML = "";

  renderAccusationTray();

  document.querySelectorAll("#accusation-modal .slot-drop").forEach((slotEl) => {
    slotEl.ondragover = (ev) => {
      ev.preventDefault();
      slotEl.classList.add("drag-over");
    };
    slotEl.ondragleave = () => slotEl.classList.remove("drag-over");
    slotEl.ondrop = (ev) => {
      ev.preventDefault();
      slotEl.classList.remove("drag-over");
      const data = JSON.parse(ev.dataTransfer.getData("text/plain"));
      const accepts = slotEl.dataset.accepts;
      if (data.type !== accepts) {
        toast(`That doesn't belong in that slot.`);
        return;
      }
      const slotName = slotEl.parentElement.dataset.slot;
      state.accusation[slotName] = data.slug;
      slotEl.innerHTML = "";
      const filled = document.createElement("div");
      filled.className = `tray-card card-type-${data.type} placed`;
      filled.textContent = data.name;
      slotEl.appendChild(filled);
      renderAccusationTray();
    };
    slotEl.addEventListener("click", () => {
      const slotName = slotEl.parentElement.dataset.slot;
      state.accusation[slotName] = null;
      slotEl.innerHTML = "";
      renderAccusationTray();
    });
  });

  document.getElementById("accusation-modal").classList.remove("hidden");
}

function renderAccusationTray() {
  const tray = document.getElementById("accusation-tray");
  tray.innerHTML = "";
  const placedSlugs = new Set(Object.values(state.accusation).filter(Boolean));
  const eligible = state.board.nodes.filter(
    (n) => (n.type === "Suspect" || n.type === "Clue") && !placedSlugs.has(n.slug)
  );
  for (const n of eligible) {
    const card = document.createElement("div");
    card.className = `tray-card card-type-${n.type}`;
    card.textContent = n.name;
    card.draggable = true;
    card.dataset.slug = n.slug;
    card.dataset.type = n.type;
    card.addEventListener("dragstart", (ev) => {
      ev.dataTransfer.setData("text/plain", JSON.stringify({ slug: n.slug, type: n.type, name: n.name }));
    });
    tray.appendChild(card);
  }
}

async function onSubmitAccusation() {
  const { culprit, motive, opportunity, means } = state.accusation;
  if (!culprit) {
    toast("You must name a culprit.");
    return;
  }
  try {
    const result = await post("/api/accuse", {
      culprit,
      motive_clue: motive,
      opportunity_clue: opportunity,
      means_clue: means,
    });
    renderVerdict(result);
    if (result.verdict === "SOLVED") {
      const culpritNode = state.board.nodes.find((n) => n.slug === culprit);
      log(`CASE SOLVED. ${culpritNode ? culpritNode.name : culprit} stands accused, and the chain holds.`, "log-breakthrough");
    } else {
      log(`Accusation returned: ${result.verdict}`, "log-error");
    }
    await refreshBoard();
  } catch (e) {
    log("Error: " + e.message, "log-error");
  }
}

function renderVerdict(result) {
  const box = document.getElementById("verdict-box");
  box.classList.remove("hidden");
  const lines = Object.entries(result.links)
    .map(([slot, r]) => `<li class="${r.valid ? "valid" : "invalid"}">${slot}: ${r.valid ? "confirmed" : r.reason}</li>`)
    .join("");
  box.innerHTML = `<h3 class="verdict-${result.verdict}">${result.verdict}</h3><ul class="verdict-links">${lines}</ul>`;
}

// ---------------------------------------------------------------------------

boot();
