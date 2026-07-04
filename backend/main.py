"""
FastAPI app for The Cognee Case Files.

Every route is a thin wrapper around graph_store.GraphStore -- the graph
IS the game engine. Routes never contain game logic themselves; they read
or write the truth/player-known/submitted-chain graphs and, where the
README calls for it, ask the LLM to narrate what cognee just revealed.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.cases import CASE_LIST, DEFAULT_CASE_ID
from backend.graph_store import GraphStore
from backend.interrogation import narrate_discovery, narrate_interrogation

store = GraphStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await store.initialize(DEFAULT_CASE_ID)
    yield


app = FastAPI(title="The Cognee Case Files", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Read-only case data (safe to expose in full -- no solution info)
# ---------------------------------------------------------------------------


@app.get("/api/cases")
async def list_cases():
    return {"cases": CASE_LIST, "active": store.case_id}


@app.get("/api/briefing")
async def briefing():
    case = store.case
    victim = case.NODES[case.VICTIM_SLUG]
    return {
        "case_id": case.CASE_ID,
        "title": case.CASE_TITLE,
        "victim": {"name": victim.name, "description": victim.description},
        "scene": case.NODES[case.SCENE_SLUG].name,
        "time_of_death": case.TIME_OF_DEATH,
        "summary": case.SUMMARY,
        "suspects": [
            {"slug": s, "name": case.NODES[s].name, "role": case.NODES[s].role}
            for s in case.SUSPECTS
        ],
        "locations": [
            {"slug": l, "name": case.NODES[l].name, "description": case.NODES[l].description}
            for l in case.LOCATIONS
        ],
    }


@app.get("/api/board")
async def board():
    return await store.board_state()


# ---------------------------------------------------------------------------
# Investigation
# ---------------------------------------------------------------------------


@app.post("/api/investigate/{location_slug}")
async def investigate(location_slug: str):
    try:
        result = await store.investigate(location_slug)
    except ValueError as e:
        raise HTTPException(404, str(e))
    result["narration"] = narrate_discovery(store.case, store.case.NODES[location_slug].name, result["new_clues"])
    return result


# ---------------------------------------------------------------------------
# Interrogation
# ---------------------------------------------------------------------------


@app.get("/api/suspects/{suspect_slug}/topics")
async def topics(suspect_slug: str):
    if suspect_slug not in store.case.SUSPECTS:
        raise HTTPException(404, f"Unknown suspect: {suspect_slug}")
    return {"topics": store.topics_for(suspect_slug)}


class InterrogateRequest(BaseModel):
    suspect: str
    topic: str


@app.post("/api/interrogate")
async def interrogate(req: InterrogateRequest):
    try:
        result = await store.interrogate(req.suspect, req.topic)
    except ValueError as e:
        raise HTTPException(404, str(e))
    result["narration"] = narrate_interrogation(store.case, req.suspect, req.topic, result["statement"], result["new_clues"])
    if result["statement"]:
        # is_lie is for LLM/narration use only -- never ship the answer to the client.
        result["statement"] = {k: v for k, v in result["statement"].items() if k != "is_lie"}
    return result


class ConfrontRequest(BaseModel):
    statement_slug: str


@app.post("/api/confront")
async def confront(req: ConfrontRequest):
    try:
        return await store.confront(req.statement_slug)
    except ValueError as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# Accusation
# ---------------------------------------------------------------------------


class AccuseRequest(BaseModel):
    culprit: str
    motive_clue: str | None = None
    opportunity_clue: str | None = None
    means_clue: str | None = None


@app.post("/api/accuse")
async def accuse(req: AccuseRequest):
    try:
        return await store.validate_accusation(req.culprit, req.motive_clue, req.opportunity_clue, req.means_clue)
    except ValueError as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------------
# Hints
# ---------------------------------------------------------------------------


@app.get("/api/hint")
async def hint():
    return await store.get_hint()


# ---------------------------------------------------------------------------
# New game
# ---------------------------------------------------------------------------


class NewGameRequest(BaseModel):
    case_id: str | None = None


@app.post("/api/new-game")
async def new_game(req: NewGameRequest | None = None):
    case_id = req.case_id if req else None
    if case_id and case_id not in {c["id"] for c in CASE_LIST}:
        raise HTTPException(404, f"Unknown case: {case_id}")
    await store.initialize(case_id)
    return await store.board_state()


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
