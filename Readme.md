# The Cognee Case Files

A Sherlock-style deduction game where a **knowledge graph is the game engine**. The entire mystery is a graph stored and reasoned over by **cognee**. The player investigates a manor, interrogates suspects, catches them lying by detecting contradictions in the graph, and wins by submitting a valid *deductive chain* — not by guessing the killer.

Cognee is the heart of the project. It holds the truth, constrains what suspects can say, detects contradictions, validates the player's reasoning, and generates hints via graph pathfinding. The LLM is a supporting actor only.

---

## 1. Build Priority (READ FIRST — scope guard)

This is a 3-day build. Build in this exact order. Each layer must work before starting the next. If time runs out, a working game with a plain board beats a beautiful board that doesn't play.

1. **Case data + cognee integration** — load Case #1 (below) into cognee as the truth graph. Verify traversal, node reveal, and consistency queries work.
2. **Core game loop backend** — investigate (reveal nodes), interrogate (LLM suspect constrained by graph), player-known graph updates.
3. **Contradiction detection** — surface conflicting edges, confront-the-suspect flow.
4. **Accusation validation** — the deductive-chain check (SOLVED / INCOMPLETE / WRONG). This is the win condition and must be rock-solid.
5. **Hints** — cognee pathfinding from known-graph to solution.
6. **UI: functional first** — plain evidence board, clickable rooms, interrogation panel, accusation panel. Playable end to end.
7. **UI: atmosphere last** — Victorian styling, red-string animations, contradiction drama, drag-to-slot accusation. Polish only after the game is fully playable.

Do NOT start the fancy animations until steps 1–6 are working.

---

## 2. Core Architecture — cognee juggles three graphs

**1. Truth graph** — the full hidden case. Loaded into cognee at startup.
- Node types: `Suspect`, `Location`, `Weapon` (means), `Motive`, `TimelineEvent`, `Clue`, `Statement`.
- Edge types: `was-at`, `had-motive`, `owned`, `seen-by`, `contradicts`, `supports`, `occurred-at`.
- The **solution** is one subgraph: `Killer → had-motive → had-opportunity (was-at scene at time-of-death) → had-means (owned weapon)`.
- Contains red herrings (suspects with motive but a solid alibi) and planted lies (a suspect asserts a false edge that contradicts the truth graph).

**2. Player-known graph** — everything the player has uncovered so far. Every investigation and interrogation reveals truth-graph nodes/edges into this graph. Drives the evidence board and the hint system. Kept separate from the truth graph.

**3. Submitted-chain graph** — the player's final accusation, validated against the truth graph.

The clean separation of these three graphs is the intellectual centerpiece — keep them clearly delineated in code.

---

## 3. Game Loop

1. **Briefing** — show the crime (victim, scene, time of death). Reveal only public nodes.
2. **Investigate** — player clicks rooms of the manor to collect clues; each click reveals truth-graph nodes/edges into the player-known graph.
3. **Interrogate** — the LLM roleplays each suspect. **Every answer must be constrained by facts retrieved from cognee** — an innocent suspect can never accidentally contradict established truth. Liars and the killer are scripted to assert specific false edges (their alibi lies). Their statements enter the player-known graph as `claimed` edges.
4. **Catch contradictions (core fun mechanic)** — when the player-known graph contains two conflicting edges (a `claimed` edge vs. an established truth edge, linked by a `contradicts` relation), cognee's consistency check surfaces "these cannot both be true." The player confronts the suspect, the lie collapses, and the true edge is revealed.
5. **Accuse (win condition)** — the player submits a deductive chain: `{culprit, motive, opportunity, means}`, each link backed by a clue node they have actually found. Cognee validates:
   - (a) Is every link a real edge in the truth graph? (no fabrication allowed)
   - (b) Is the chain complete — motive AND opportunity AND means all present?
   - (c) Does it resolve to the true killer subgraph?
   - Returns exactly one of: **SOLVED** (valid + complete + correct), **INCOMPLETE** (name what's missing, e.g. "no motive established"), or **WRONG** (chain points to the wrong suspect).
   - Guessing the killer WITHOUT a complete valid chain must NOT count as solved.
6. **Hints** — cognee finds the shortest path from the player-known graph to an unexplored solution node and nudges the player (e.g. "You've never established where the gardener was at 9pm").

---

## 4. Tech Stack

- **Backend:** Python, FastAPI.
- **Graph/memory layer:** **cognee** — store all three graphs, run traversal for clue reveals, consistency checks for contradictions, and pathfinding for hints. Do NOT reimplement graph logic outside cognee where cognee can do it. This is a hard requirement — cognee must be doing the graph work.
- **LLM:** provider-agnostic. Use a single `LLM_API_KEY` environment variable and an easily swappable client wrapper (`llm_client.py`) with one function `def ask_llm(system, messages) -> str`. Do not hardcode any provider. The developer will add the key and provider at the end. The LLM is used for two jobs ONLY:
  - (a) suspect roleplay, constrained by graph-retrieved facts,
  - (b) narrating clue discoveries in atmospheric prose.
  - The LLM NEVER decides guilt. All verdict logic is pure graph validation in cognee.
- **Frontend:** single-page app. Vanilla JS + HTML/CSS is fine, or a light framework — keep it simple and self-contained. No heavy build tooling.
- **Config:** `.env` for `LLM_API_KEY`. README section explaining how to add it.

---

## 5. UI Spec — Victorian detective's study / evidence corkboard

Make it genuinely atmospheric and fun. Aesthetic and mechanics:

- **Mood:** dark wood-panelled study, warm gaslamp lighting, aged-paper textures. Sepia / amber / deep-green palette. Subtle vignette and paper grain. Serif display font (e.g. Fraunces or a Victorian serif) for headings; a clean readable body font.
- **Evidence board (the hero UI):** a corkboard where discovered clues appear as pinned index cards and photos. **Red string literally connects related nodes** as the player establishes edges — this IS the player-known graph, visualized. New connections animate the string being pinned.
- **Locations:** a hand-drawn-map-style navigation of the manor (clickable rooms) — gives a light escape-room / explore feel.
- **Interrogation:** the suspect appears as a portrait card in a dialogue panel; the player picks from suggested questions or types their own; contradictions highlight in red.
- **Contradiction moment:** make it dramatic — conflicting cards flash, red string snaps taut between them, a "CONTRADICTION" stamp appears.
- **Accusation:** a "Final Deduction" panel where the player drags clue-cards into four slots — **Culprit / Motive / Opportunity / Means** — to assemble their chain. Submitting animates cognee validating each link green (valid) or red (invalid/missing).
- Single-page, responsive, smooth transitions. Prioritize atmosphere and the red-string board — that is the demo money-shot.

Remember: functional board first, animated board last (see Build Priority).

---

## 6. Case #1 — "A Death at Thornfield Manor" (fully authored)

Load this as the truth graph. It has exactly one valid solution chain.

### The crime
- **Victim:** Lord Edmund Thornfield, found dead in the **Study** at approximately **9:00 PM**.
- **Cause of death:** blunt-force trauma. The coroner establishes time of death at **9:00 PM**.
- **Public facts (revealed at briefing):** the victim was killed in the Study around 9 PM; the household of six was home that evening; a storm knocked the power out from 8:45–9:15 PM.

### Suspects (6)
1. **Mrs. Agnes Hale** — the housekeeper. 20 years of service.
2. **Mr. Julian Thornfield** — the victim's nephew and heir.
3. **Dr. Silas Croft** — the family physician, present as a dinner guest.
4. **Miss Eleanor Vance** — the victim's private secretary.
5. **Mr. Thomas Byrne** — the groundskeeper/gardener.
6. **Mrs. Cordelia Thornfield** — the victim's estranged wife.

### The solution (the true killer subgraph)
**Killer: Miss Eleanor Vance (the secretary).**
- **Motive:** the victim had discovered she was embezzling estate funds and planned to report her the next morning (`had-motive: fear_of_exposure`).
- **Opportunity:** she was in the Study at 9 PM. She claims she was in the Library, but the Library was locked from the outside at 8:40 PM (a clue), so she could not have been there — placing her in the Study during the blackout.
- **Means:** the murder weapon is a heavy brass candlestick from the Study. Eleanor's gloves (found, bloodstained, hidden in the Library returns basket) tie her to handling it (`owned/handled: brass_candlestick`).

### Red herrings (real suspects with real motive but blocked)
- **Julian Thornfield (heir):** strong motive (inheritance), BUT a solid alibi — he was seen by Dr. Croft in the Billiard Room continuously from 8:30–9:30 PM (`seen-by: Dr_Croft`). Motive present, opportunity blocked.
- **Mrs. Cordelia Thornfield (estranged wife):** strong motive (bitter divorce, cut from the will), BUT she had already left for the train station at 8:15 PM — the stationmaster's ticket stub is a clue (`was-at: train_station`). Motive present, opportunity blocked.
- **Thomas Byrne (gardener):** appears suspicious (muddy boots, seen near the Study window) BUT he was fixing the fuse box during the blackout, corroborated by Mrs. Hale (`seen-by: Agnes_Hale`). Suspicious clue, innocent.

### Planted lies (the contradiction mechanic)
1. **Eleanor's alibi lie:** she claims "I was in the Library from 8:30 until the body was found." The truth graph has the Library locked from outside at 8:40 PM (clue: `library_locked_stub`). Her claim `Eleanor was-at Library @9PM` `contradicts` the truth `Library locked-from-outside @8:40PM`. Catching this collapses her alibi.
2. **Julian's small lie:** he claims he "never left the Billiard Room all evening," but a footman saw him fetch a drink at 9:05 — a minor contradiction that turns out to be a harmless lie (he was embarrassed about drinking). This is a *decoy contradiction*: it resolves to nothing, teaching the player that not every lie is the murder.

### Clues (revealed by investigating rooms)
- `brass_candlestick` (Study) — the murder weapon, one candlestick missing from a matched pair.
- `embezzlement_ledger` (Study desk) — hidden accounts showing Eleanor's theft → establishes her motive.
- `library_locked_stub` (Library door) — the Library was bolted from the outside at 8:40 PM → breaks Eleanor's alibi.
- `bloodstained_gloves` (Library returns basket) — Eleanor's gloves, hidden → ties her to the weapon.
- `train_ticket_stub` (Hall table) — Cordelia's 8:15 departure → clears Cordelia.
- `fuse_box_note` (Cellar) — confirms Byrne was fixing the fuse during blackout → clears Byrne.
- `billiard_witness` (from Dr. Croft interrogation) — clears Julian's opportunity.

### The one valid winning chain
- **Culprit:** Eleanor Vance
- **Motive:** `embezzlement_ledger` → fear of exposure
- **Opportunity:** `library_locked_stub` (breaks her alibi, places her in the Study during blackout)
- **Means:** `bloodstained_gloves` + `brass_candlestick`

Any accusation missing one of these three (motive/opportunity/means) returns **INCOMPLETE**. Any accusation naming a different culprit returns **WRONG**. Only the full correct chain returns **SOLVED**.

---

## 7. Deliverables

- A working, playable game with Case #1 complete and end-to-end.
- Clear code separation of the three graphs (truth / player-known / submitted-chain) in the cognee integration.
- A provider-agnostic `llm_client.py` wrapper so the developer can drop in any LLM key/provider at the end.
- A short section in the code's own docs (or comments) explaining exactly how cognee powers each mechanic: reveal (traversal), contradiction (consistency check), validation (subgraph match), hint (pathfinding).
- Instructions to run locally and where to add the `LLM_API_KEY`.

---

## 8. Notes for the builder

- Keep it to ONE case, ONE solution, SIX suspects. Do not add case generation or multiple solutions — out of scope for the timeline.
- The LLM must never be the judge. Every verdict is graph logic. If you find yourself asking the LLM "is this the killer?", stop — that belongs in cognee validation.
- Prefer letting cognee do graph traversal, consistency checks, and pathfinding over writing custom graph code alongside it. Cognee being visibly central is a hard requirement.
- Build functional before beautiful. A plain playable board on day 3 is a win; a gorgeous broken one is not.
