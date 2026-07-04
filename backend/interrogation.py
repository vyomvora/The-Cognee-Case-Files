"""
Suspect roleplay: turns graph facts into atmospheric first-person prose.

The LLM only ever narrates facts that graph_store.py has already retrieved
from cognee (a suspect's persona + their one scripted statement for the topic
asked). It never invents an alibi, never decides truth, and can't accidentally
contradict the truth graph -- the actual `claimed` edges are written to the
player-known graph by graph_store.interrogate() regardless of what the LLM
says here. This function only dresses up the delivery.

Both functions take the active case module (see backend/cases/*.py) so the
same narration logic works for any of the three cases.
"""

from backend.llm_client import ask_llm


def narrate_interrogation(case, suspect_slug: str, topic_id: str, statement_view: dict | None, new_clues: list[dict]) -> str:
    suspect = case.NODES[suspect_slug]
    topic_label = next(
        (t["label"] for t in case.INTERROGATION_TOPICS[suspect_slug] if t["id"] == topic_id),
        topic_id,
    )
    victim = case.NODES[case.VICTIM_SLUG]

    facts = []
    if statement_view:
        facts.append(f'Your scripted answer to give (say this, in character, do not contradict it): "{statement_view["text"]}"')
    for clue in new_clues:
        facts.append(f"This answer also reveals a detail: {clue['description']}")
    if not facts:
        facts.append("You have nothing new to add on this topic -- deflect politely, in character, without revealing anything.")

    system = (
        f"You are {suspect.name}, {suspect.role}, being questioned about the death of "
        f"{victim.name}. Who you are: {suspect.description}\n"
        "Stay in character. Use plain, simple, everyday English -- short sentences, no fancy or "
        "old-fashioned words. Reply in 2-4 sentences. "
        "You may ONLY say the facts listed below -- never invent an alibi, a name, or a time "
        "that isn't given to you. If a fact is marked as your scripted answer, your reply must "
        "say exactly that, in your own words."
    )
    user = f"The detective asks you about: {topic_label}\n\nFacts you must work from:\n" + "\n".join(f"- {f}" for f in facts)

    return ask_llm(system, [{"role": "user", "content": user}])


def narrate_discovery(case, location_or_suspect: str, clues: list[dict]) -> str:
    if not clues:
        return ""
    system = (
        "You are the narrator of a detective game, describing what the player's character "
        "notices. Use plain, simple, everyday English -- short sentences, no fancy or "
        "old-fashioned words. Reply in 2-3 sentences total. Do not add facts beyond what is "
        "listed -- only describe them clearly."
    )
    clue_lines = "\n".join(f"- {c['name']}: {c['description']}" for c in clues)
    user = f"The detective searches {location_or_suspect} and finds:\n{clue_lines}"
    return ask_llm(system, [{"role": "user", "content": user}])
