# The Cognee Case Files

A murder mystery game where a knowledge graph is the actual brain of the game — built with **Cognee**.

You play a detective. Someone died at Thornfield Manor. You walk through rooms, find clues, question suspects, catch them lying, and try to prove who did it — with real evidence, not just a guess.

---

## What makes this different

Most mystery games are scripted. This one runs on a graph.

- The whole case — suspects, motives, alibis, secrets, lies — lives inside Cognee as a knowledge graph.
- When you search a room, Cognee reveals real facts from that graph onto your evidence board.
- When you talk to a suspect, the AI can only say things that match the graph, so no one can accidentally say something untrue.
- If a suspect lies, Cognee catches it, because the lie clashes with a fact already in the graph.
- When you make your final accusation, Cognee checks your whole chain of reasoning (culprit, motive, opportunity, means) against the truth graph. It only says "solved" if every piece is correct and backed by real evidence.

The AI is only there to talk like a suspect and describe scenes. It never decides who's guilty — Cognee does.

---

## How Cognee is used

- **Truth graph** — the full hidden case, with the real story. Never shown to the player directly.
- **Player-known graph** — everything you've actually discovered so far. This is what draws your evidence board.
- **Submitted-chain graph** — your final accusation, rebuilt fresh every time you submit, so Cognee can check it against the truth graph.

Cognee handles:
- Revealing clues (graph traversal)
- Catching lies (checking for contradicting facts)
- Checking your final accusation (does your evidence really lead to the killer?)
- Giving hints (finding what part of the solution you haven't found yet)

---

## Tech stack

- **Backend:** Python + FastAPI
- **Graph engine:** Cognee
- **AI:** any LLM you want, swappable through one `.env` file
- **Frontend:** plain HTML, CSS, JavaScript — no framework, no build step

---

## How to run it

1. Clone or download this project.
2. Open a terminal in the project folder.
3. Install the requirements:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env`:
   ```
   cp .env.example .env
   ```
5. Open `.env` and fill in:
   - `LLM_PROVIDER` (e.g. `openai`)
   - `LLM_MODEL` (e.g. `gpt-4o-mini`)
   - `LLM_API_KEY` (your own API key)
6. Start the server:
   ```
   uvicorn backend.main:app --reload
   ```
7. Open your browser and go to:
   ```
   http://localhost:8000
   ```
8. Pick a case and start investigating.

---

## Cases included

- A Death at Thornfield Manor
- Murder on the Night Train
- Death at the Gallery
