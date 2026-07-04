"""
The three graphs, all backed by cognee.

- ``truth``: the full hidden case, loaded once per game. Never mutated
  during play. The single source of truth for "what really happened."
- ``player_known``: everything the player has actually uncovered. Built
  incrementally by investigate()/interrogate()/confront() as cognee node/edge
  inserts -- never by copying Python dicts around.
- ``submitted_chain``: rebuilt fresh on every accusation attempt from exactly
  what the player dragged into the four slots, then checked against ``truth``.

Every mechanic in the README maps to a cognee call here:
  - reveal            -> truth graph traversal (get_connections) feeding
                          player_known.add_node / add_edge
  - contradiction      -> truth.has_edge(...,"contradicts") gates a
                          presence check against player_known
  - accusation         -> submitted_chain built from the player's picks,
                          each link checked with truth.has_edge(...)
  - hint               -> truth.get_connections() from an unfound solution
                          clue back to the location/suspect that unlocks it

GraphStore is parameterized by *case*: initialize(case_id) loads exactly one
case module (backend/cases/case1.py etc.) into the truth graph and resets
player-known/submitted-chain. Only one case is ever active at a time.
"""

import os
from typing import Any, Optional

from cognee.infrastructure.databases.graph.ladybug.adapter import LadybugAdapter

from backend.cases import CASES, DEFAULT_CASE_ID
from backend.schema import Clue

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class GraphStore:
    """Owns the three cognee graph engines and all game-state derived from them."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.truth = LadybugAdapter(db_path=os.path.join(DATA_DIR, "truth_graph"))
        self.player_known = LadybugAdapter(db_path=os.path.join(DATA_DIR, "player_known_graph"))
        self.submitted_chain = LadybugAdapter(db_path=os.path.join(DATA_DIR, "submitted_chain_graph"))
        self.case = None
        self.case_id = None

    def _slug_id(self, slug: str) -> str:
        return str(self.case.NODES[slug].id)

    # -- setup -----------------------------------------------------------------

    async def initialize(self, case_id: Optional[str] = None):
        """Wipe all three graphs and load the given case fresh. Switching cases is just a reload."""
        case_id = case_id or self.case_id or DEFAULT_CASE_ID
        self.case = CASES[case_id]
        self.case_id = case_id

        for engine in (self.truth, self.player_known, self.submitted_chain):
            try:
                await engine.delete_graph()
            except Exception:
                pass

        self._slug_to_id = {slug: str(node.id) for slug, node in self.case.NODES.items()}
        self._id_to_slug = {v: k for k, v in self._slug_to_id.items()}

        self._edge_by_triple = {
            (src, dst, rel): props for src, dst, rel, props in self.case.EDGES
        }
        self._unlock_index: dict[str, list[tuple[str, str, str]]] = {}
        for src, dst, rel, props in self.case.EDGES:
            for clue_slug in props.get("unlocked_by", []):
                self._unlock_index.setdefault(clue_slug, []).append((src, dst, rel))
        self._contradictions = [
            (src, dst, props)
            for src, dst, rel, props in self.case.EDGES
            if rel == "contradicts"
        ]  # (statement_slug, clue_slug, props)

        self._revealed_node_slugs: set[str] = set()
        self._revealed_edge_triples: set[tuple[str, str, str]] = set()
        self._revealed_clue_slugs: set[str] = set()
        self._discussed_topics: set[tuple[str, str]] = set()
        self._resolved_contradictions: set[str] = set()
        self._solved = False

        await self.truth.add_nodes(list(self.case.NODES.values()))
        edge_tuples = [
            (self._slug_id(src), self._slug_id(dst), rel, props) for src, dst, rel, props in self.case.EDGES
        ]
        await self.truth.add_edges(edge_tuples)

        await self._reveal_nodes(self.case.BRIEFING_NODE_SLUGS)
        for src, dst, rel, props in self.case.EDGES:
            if props.get("public"):
                await self._reveal_edge(src, dst, rel)

    # -- low-level reveal helpers ------------------------------------------------

    async def _reveal_node(self, slug: str) -> bool:
        if slug in self._revealed_node_slugs:
            return False
        node = self.case.NODES[slug]
        await self.player_known.add_nodes([node])
        self._revealed_node_slugs.add(slug)
        if isinstance(node, Clue):
            self._revealed_clue_slugs.add(slug)
        return True

    async def _reveal_nodes(self, slugs: list[str]) -> list[str]:
        newly = []
        for slug in slugs:
            if await self._reveal_node(slug):
                newly.append(slug)
        return newly

    async def _reveal_edge(self, src: str, dst: str, rel: str) -> bool:
        triple = (src, dst, rel)
        if triple in self._revealed_edge_triples:
            return False
        await self._reveal_node(src)
        await self._reveal_node(dst)
        props = self._edge_by_triple.get(triple, {})
        await self.player_known.add_edges([(self._slug_id(src), self._slug_id(dst), rel, props)])
        self._revealed_edge_triples.add(triple)
        return True

    async def _cascade_unlocks(self, clue_slug: str) -> dict[str, list]:
        """Reveal any truth-graph edges gated behind this clue (skipping confront-only ones)."""
        revealed_nodes, revealed_edges = [], []
        for src, dst, rel in self._unlock_index.get(clue_slug, []):
            props = self._edge_by_triple.get((src, dst, rel), {})
            if props.get("confront_only"):
                continue
            for slug in (src, dst):
                if slug not in self._revealed_node_slugs:
                    revealed_nodes.append(slug)
            if await self._reveal_edge(src, dst, rel):
                revealed_edges.append({"source": src, "target": dst, "relation": rel})
        return {"nodes": revealed_nodes, "edges": revealed_edges}

    # -- investigation -----------------------------------------------------------

    def clues_at_location(self, location_slug: str) -> list[str]:
        return [
            slug
            for slug, node in self.case.NODES.items()
            if isinstance(node, Clue) and node.source_type == "location" and node.source_id == location_slug
        ]

    async def investigate(self, location_slug: str) -> dict[str, Any]:
        if location_slug not in self.case.LOCATIONS:
            raise ValueError(f"Unknown location: {location_slug}")

        new_clues = []
        cascade_nodes, cascade_edges = [], []
        for clue_slug in self.clues_at_location(location_slug):
            if clue_slug in self._revealed_clue_slugs:
                continue
            await self._reveal_node(clue_slug)
            await self._reveal_edge(location_slug, clue_slug, "found-at")
            new_clues.append(clue_slug)
            cascade = await self._cascade_unlocks(clue_slug)
            cascade_nodes += cascade["nodes"]
            cascade_edges += cascade["edges"]

        return {
            "location": location_slug,
            "new_clues": [self._clue_view(c) for c in new_clues],
            "cascade_nodes": cascade_nodes,
            "cascade_edges": cascade_edges,
            "contradictions": await self.check_contradictions(),
        }

    # -- interrogation -------------------------------------------------------------

    def topics_for(self, suspect_slug: str) -> list[dict]:
        return self.case.INTERROGATION_TOPICS.get(suspect_slug, [])

    async def interrogate(self, suspect_slug: str, topic_id: str) -> dict[str, Any]:
        topics = {t["id"]: t for t in self.topics_for(suspect_slug)}
        if topic_id not in topics:
            raise ValueError(f"Unknown topic {topic_id} for {suspect_slug}")
        topic = topics[topic_id]
        self._discussed_topics.add((suspect_slug, topic_id))

        statement_view = None
        if topic["statement"]:
            stmt_slug = topic["statement"]
            statement = self.case.NODES[stmt_slug]
            await self._reveal_edge(suspect_slug, stmt_slug, "made-statement")
            claims_edges = [
                (s, d, r) for s, d, r in self._edges_from(stmt_slug, "claims")
            ]
            for s, d, r in claims_edges:
                await self._reveal_edge(s, d, r)
            statement_view = {
                "slug": stmt_slug,
                "text": statement.text,
                "is_lie": statement.is_lie,  # for the LLM prompt only; never shown to the player
            }

        cascade_nodes, cascade_edges = [], []
        new_clues = []
        for clue_slug in topic.get("reveals", []):
            if clue_slug in self._revealed_clue_slugs:
                continue
            await self._reveal_node(clue_slug)
            await self._reveal_edge(suspect_slug, clue_slug, "revealed-by")
            new_clues.append(clue_slug)
            cascade = await self._cascade_unlocks(clue_slug)
            cascade_nodes += cascade["nodes"]
            cascade_edges += cascade["edges"]

        return {
            "suspect": suspect_slug,
            "topic": topic_id,
            "statement": statement_view,
            "new_clues": [self._clue_view(c) for c in new_clues],
            "cascade_nodes": cascade_nodes,
            "cascade_edges": cascade_edges,
            "contradictions": await self.check_contradictions(),
        }

    def _edges_from(self, src_slug: str, rel: str) -> list[tuple[str, str, str]]:
        return [(s, d, r) for s, d, r, _ in self.case.EDGES if s == src_slug and r == rel]

    def _clue_view(self, slug: str) -> dict:
        clue: Clue = self.case.NODES[slug]
        return {"slug": slug, "name": clue.name, "description": clue.description}

    # -- contradictions ------------------------------------------------------------

    async def check_contradictions(self) -> list[dict]:
        """Ask cognee: for each authored contradiction, are both sides now present
        in the player-known graph, and has the player not yet confronted it?"""
        active = []
        for statement_slug, clue_slug, props in self._contradictions:
            if statement_slug in self._resolved_contradictions:
                continue
            statement_id = self._slug_id(statement_slug)
            clue_id = self._slug_id(clue_slug)
            # Ground truth: cognee confirms this pair really does conflict.
            is_true_contradiction = await self.truth.has_edge(statement_id, clue_id, "contradicts")
            if not is_true_contradiction:
                continue
            statement_known = (await self.player_known.get_node(statement_id)) is not None
            clue_known = (await self.player_known.get_node(clue_id)) is not None
            if statement_known and clue_known:
                statement = self.case.NODES[statement_slug]
                clue = self.case.NODES[clue_slug]
                active.append(
                    {
                        "statement_slug": statement_slug,
                        "speaker": statement.speaker,
                        "statement_text": statement.text,
                        "clue_slug": clue_slug,
                        "clue_name": clue.name,
                        "clue_description": clue.description,
                        "decoy": bool(props.get("decoy")),
                    }
                )
        return active

    async def confront(self, statement_slug: str) -> dict[str, Any]:
        active = {c["statement_slug"]: c for c in await self.check_contradictions()}
        if statement_slug not in active:
            raise ValueError("No active, unresolved contradiction for that statement.")

        reveal_info = self.case.CONFRONT_REVEALS.get(statement_slug, {"reveal_edges": [], "narration_hint": ""})
        revealed_edges = []
        for src, dst, rel in reveal_info["reveal_edges"]:
            await self._reveal_edge(src, dst, rel)
            revealed_edges.append({"source": src, "target": dst, "relation": rel})

        self._resolved_contradictions.add(statement_slug)

        return {
            "statement_slug": statement_slug,
            "decoy": active[statement_slug]["decoy"],
            "narration_hint": reveal_info["narration_hint"],
            "revealed_edges": revealed_edges,
        }

    # -- board state -----------------------------------------------------------------

    async def board_state(self) -> dict[str, Any]:
        nodes, edges = await self.player_known.get_graph_data()
        node_views = []
        for node_id, props in nodes:
            slug = self._id_to_slug.get(node_id, node_id)
            # Ship every stored field except internal/spoiler ones -- Statement.text,
            # TimelineEvent.time etc. all need to reach the board; is_lie must never.
            visible = {k: v for k, v in props.items() if k not in ("is_lie", "id")}
            node_views.append({"slug": slug, **visible})
        edge_views = []
        for src_id, dst_id, rel, props in edges:
            edge_views.append(
                {
                    "source": self._id_to_slug.get(src_id, src_id),
                    "target": self._id_to_slug.get(dst_id, dst_id),
                    "relation": rel,
                    "properties": {k: v for k, v in props.items() if k not in ("unlocked_by",)},
                }
            )
        return {
            "case_id": self.case_id,
            "nodes": node_views,
            "edges": edge_views,
            "contradictions": await self.check_contradictions(),
            "solved": self._solved,
        }

    # -- accusation / validation ------------------------------------------------------

    async def validate_accusation(
        self, culprit_slug: str, motive_clue: Optional[str], opportunity_clue: Optional[str], means_clue: Optional[str]
    ) -> dict[str, Any]:
        if culprit_slug not in self.case.SUSPECTS:
            raise ValueError(f"Unknown suspect: {culprit_slug}")

        # Rebuild the submitted-chain graph from scratch every attempt.
        await self.submitted_chain.delete_graph()
        submitted_slugs = [s for s in (culprit_slug, motive_clue, opportunity_clue, means_clue) if s]
        await self.submitted_chain.add_nodes([self.case.NODES[s] for s in submitted_slugs])
        slot_edges = [
            (motive_clue, "motive"),
            (opportunity_clue, "opportunity"),
            (means_clue, "means"),
        ]
        chain_edges = [
            (self._slug_id(culprit_slug), self._slug_id(clue_slug), f"accuses-{slot}", {})
            for clue_slug, slot in slot_edges
            if clue_slug
        ]
        await self.submitted_chain.add_edges(chain_edges)

        results = {}
        for clue_slug, slot, relation in [
            (motive_clue, "motive", "had-motive"),
            (opportunity_clue, "opportunity", "was-at"),
            (means_clue, "means", "owned"),
        ]:
            results[slot] = await self._validate_link(culprit_slug, clue_slug, relation)

        found_all_clues = all(
            (c in self._revealed_clue_slugs) for c in (motive_clue, opportunity_clue, means_clue) if c
        )
        is_complete = found_all_clues and all(r["valid"] for r in results.values())
        resolves_to_true_killer = culprit_slug == self.case.SOLUTION["culprit"]

        if not resolves_to_true_killer:
            verdict = "WRONG"
        elif not is_complete:
            verdict = "INCOMPLETE"
        else:
            verdict = "SOLVED"
            self._solved = True

        missing = [slot for slot, r in results.items() if not r["valid"]]

        return {
            "verdict": verdict,
            "culprit": culprit_slug,
            "links": results,
            "missing": missing,
        }

    async def _validate_link(self, culprit_slug: str, clue_slug: Optional[str], relation: str) -> dict[str, Any]:
        if not clue_slug:
            return {"valid": False, "reason": "no clue submitted"}
        if clue_slug not in self._revealed_clue_slugs:
            return {"valid": False, "reason": "clue not yet found by the player"}

        clue_id = self._slug_id(clue_slug)
        # cognee traversal: what does this clue actually support in the truth graph?
        connections = await self.truth.get_connections(clue_id)
        support_targets = [
            target["id"] for source, rel, target in connections if rel.get("relationship_name") == "supports" and source["id"] == clue_id
        ]
        if not support_targets:
            return {"valid": False, "reason": "clue does not support any fact (fabricated link)"}

        culprit_id = self._slug_id(culprit_slug)
        for target_id in support_targets:
            if await self.truth.has_edge(culprit_id, target_id, relation):
                return {"valid": True, "reason": "confirmed in truth graph"}
        return {"valid": False, "reason": "clue does not connect this suspect to that fact"}

    # -- hints ------------------------------------------------------------------------

    async def get_hint(self) -> dict[str, Any]:
        for slot, info in self.case.SOLUTION.items():
            if slot == "culprit":
                continue
            clue_slug = info["clue"]
            if clue_slug in self._revealed_clue_slugs:
                continue
            clue: Clue = self.case.NODES[clue_slug]
            if clue.source_type == "location":
                place = self.case.NODES[clue.source_id]
                text = f"You've never searched {place.name} closely enough. There's something there about {slot}."
            else:
                suspect = self.case.NODES[clue.source_id]
                text = f"You haven't pressed {suspect.name} hard enough. Ask about {slot}."
            return {"slot": slot, "clue": clue_slug, "text": text}

        return {
            "slot": None,
            "clue": None,
            "text": "You have everything you need. Assemble your Final Deduction.",
        }
