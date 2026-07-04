"""
Case #2 -- "Murder on the Night Train".

Same shape as Case #1 (six suspects, one killer, three red herrings, one
real lie, one decoy lie) but a different setting, cast, and clues.
"""

from backend.schema import (
    Victim,
    Suspect,
    Location,
    Weapon,
    Motive,
    TimelineEvent,
    Clue,
    Statement,
)

CASE_ID = "case2"
CASE_TITLE = "Murder on the Night Train"
CASE_BLURB = "A rich businessman is found dead in his train compartment, late at night."

VICTIM_SLUG = "jack_reed"
SCENE_SLUG = "compartment_4"
TIME_OF_DEATH = "11:00 PM"
SUMMARY = (
    "Jack Reed, a rich businessman, was found dead in his train compartment at about 11:00 PM. "
    "He was stabbed with something sharp. Six other people were riding in his train car that night. "
    "The train made an unplanned stop from 10:45 to 11:15 PM."
)

NODES = {}


def _add(cls, slug, **fields):
    node = cls(id=cls.id_for(f"{CASE_ID}:{slug}"), **fields)
    NODES[slug] = node
    return node


# --- Victim ---

_add(
    Victim,
    "jack_reed",
    name="Jack Reed",
    description="A rich businessman. Found dead in his train compartment, stabbed with something sharp.",
)

# --- Suspects ---

_add(
    Suspect,
    "anna_reed",
    name="Anna Reed",
    role="Wife",
    description="Jack's wife. Their marriage was not a happy one.",
)
_add(
    Suspect,
    "paul_reed",
    name="Paul Reed",
    role="Brother",
    description="Jack's younger brother. Owes people money and was hoping for help from Jack.",
)
_add(
    Suspect,
    "kate_lane",
    name="Kate Lane",
    role="Secretary",
    description="Jack's secretary. Handles his letters, his meetings, and his money.",
)
_add(
    Suspect,
    "sam_fox",
    name="Sam Fox",
    role="Train Guard",
    description="Works on the train. Carries a master key to every compartment.",
)
_add(
    Suspect,
    "mia_cole",
    name="Mia Cole",
    role="Singer",
    description="A young singer, travelling alone to her next show.",
)
_add(
    Suspect,
    "ray_webb",
    name="Ray Webb",
    role="Doctor",
    description="A doctor, riding the same train. He looked at Jack's body after it was found.",
)

SUSPECTS = ["anna_reed", "paul_reed", "kate_lane", "sam_fox", "mia_cole", "ray_webb"]

# --- Locations ---

_add(Location, "compartment_4", name="Compartment 4", description="Jack's private room on the train. A desk, a small bed, and a suitcase.")
_add(Location, "dining_car", name="The Dining Car", description="Tables and chairs where passengers eat. It closes early at night.")
_add(Location, "luggage_car", name="The Luggage Car", description="Bags and cases are stored here, including Jack's briefcase.")
_add(Location, "corridor", name="The Corridor", description="The narrow hallway that runs past every compartment.")
_add(Location, "engine_room", name="The Engine Room", description="Loud and hot. The train's lights and wiring run through here.")
_add(Location, "lounge", name="The Lounge", description="A quiet room with soft chairs and a card table.")
_add(Location, "millbrook_station", name="Millbrook Station", description="A small station the train stopped at earlier in the evening.")

LOCATIONS = ["compartment_4", "dining_car", "luggage_car", "corridor", "engine_room", "lounge"]

# --- Weapon / Motive ---

_add(Weapon, "letter_opener", name="Letter Opener", description="A sharp letter opener from Jack's own desk. Normally used to open his mail.")

_add(Motive, "fear_of_arrest", name="Fear of Being Caught", description="Jack found out Kate had been stealing money from his company. He planned to fire her and call the police.")
_add(Motive, "inheritance", name="Inheritance", description="Paul owes a lot of money. He was hoping for a large gift from Jack's will.")
_add(Motive, "unhappy_marriage", name="An Unhappy Marriage", description="Anna and Jack had a troubled marriage. She would get a large amount of money if Jack died.")

# --- Timeline events ---

_add(TimelineEvent, "time_of_death", name="Time of Death", time="11:00 PM", description="The doctor says Jack died at about 11:00 PM.")
_add(TimelineEvent, "unscheduled_stop", name="The Unplanned Stop", time="10:45 PM - 11:15 PM", description="The train stopped without warning from 10:45 to 11:15 PM. People moved between cars during this time.")

# ---------------------------------------------------------------------------
# Clues
# ---------------------------------------------------------------------------

_add(Clue, "letter_opener_clue", name="The Missing Letter Opener", source_type="location", source_id="compartment_4",
     description="Jack's letter opener is missing from his desk. It's normally kept in a small tray by his papers.")
_add(Clue, "torn_note", name="A Torn Note", source_type="location", source_id="compartment_4",
     description="A torn piece of paper on the floor. It says '...will call the police in the morning about the missing funds.'")
_add(Clue, "money_report", name="A Money Report", source_type="location", source_id="luggage_car",
     description="A report in Jack's briefcase. It shows a large amount of company money is missing, and points to Kate's accounts.")
_add(Clue, "dining_log", name="The Dining Car Log", source_type="location", source_id="dining_car",
     description="A log book shows the dining car closed at 10:30 PM. No one was allowed in after that.")
_add(Clue, "fingerprint_report", name="A Fingerprint Report", source_type="interrogation", source_id="ray_webb",
     description="Dr. Webb checked the letter opener. He found clear fingerprints on the handle -- Kate's fingerprints.")
_add(Clue, "ticket_stamp", name="A Stamped Ticket", source_type="location", source_id="luggage_car",
     description="A ticket stamped 10:30 PM at Millbrook Station, in Anna's name. She got off the train before the murder.")
_add(Clue, "repair_log", name="A Repair Log", source_type="location", source_id="engine_room",
     description="A log shows Sam Fox was fixing a broken light in the engine room from 10:30 to 11:30 PM.")
_add(Clue, "master_key_log", name="Master Key Sign-Out", source_type="location", source_id="corridor",
     description="A sign-out sheet shows Sam Fox had the master key tonight. Looks bad -- until you check where he actually was.")
_add(Clue, "card_game_witness", name="Dr. Webb's Story", source_type="interrogation", source_id="ray_webb",
     description="Dr. Webb says he played cards with Paul from 10:30 until they heard shouting -- except for a few minutes when Paul stepped out for a smoke.")
_add(Clue, "paul_motive_note", name="Talk of Money Trouble", source_type="interrogation", source_id="paul_reed",
     description="Paul admits he owes a lot of money, and was counting on help from Jack's will.")
_add(Clue, "anna_motive_note", name="Talk of the Marriage", source_type="interrogation", source_id="anna_reed",
     description="Anna admits the marriage was unhappy, and that she would inherit a large sum if Jack died.")

CLUE_SLUGS = [
    "letter_opener_clue",
    "torn_note",
    "money_report",
    "dining_log",
    "fingerprint_report",
    "ticket_stamp",
    "repair_log",
    "master_key_log",
    "card_game_witness",
    "paul_motive_note",
    "anna_motive_note",
]

# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

_add(Statement, "anna_alibi", speaker="anna_reed", is_lie=False,
     name="Anna's Story",
     text="I got off the train at Millbrook, the stop before this one, around half past ten.")
_add(Statement, "paul_alibi", speaker="paul_reed", is_lie=True, decoy=True,
     name="Paul's Story",
     text="I never left the card table all night. Ask Dr. Webb, he was right there with me.")
_add(Statement, "kate_alibi", speaker="kate_lane", is_lie=True,
     name="Kate's Story",
     text="I was in the dining car from ten o'clock until they found him. I was there the whole time.")
_add(Statement, "sam_alibi", speaker="sam_fox", is_lie=False,
     name="Sam's Story",
     text="I was in the engine room fixing a broken light. I was there for the whole unplanned stop.")
_add(Statement, "mia_alibi", speaker="mia_cole", is_lie=False,
     name="Mia's Story",
     text="I was in the lounge reading. I saw the guard working on a light in the next car.")
_add(Statement, "webb_alibi", speaker="ray_webb", is_lie=False,
     name="Dr. Webb's Story",
     text="Paul and I played cards from half past ten until we heard shouting. He did step out once, for a smoke, around eleven.")

STATEMENTS = {
    "anna_reed": "anna_alibi",
    "paul_reed": "paul_alibi",
    "kate_lane": "kate_alibi",
    "sam_fox": "sam_alibi",
    "mia_cole": "mia_alibi",
    "ray_webb": "webb_alibi",
}

# ---------------------------------------------------------------------------
# Edges
# ---------------------------------------------------------------------------

EDGES = [
    # Public briefing facts.
    ("time_of_death", "compartment_4", "occurred-at", {"public": True}),
    ("jack_reed", "compartment_4", "was-at", {"public": True}),
    ("unscheduled_stop", "compartment_4", "occurred-at", {"public": True}),

    # --- The solution chain (Kate Lane) ---
    ("kate_lane", "fear_of_arrest", "had-motive", {"unlocked_by": ["money_report"]}),
    ("kate_lane", "compartment_4", "was-at", {"time": "11:00 PM", "unlocked_by": ["dining_log"], "confront_only": True}),
    ("kate_lane", "letter_opener", "owned", {"unlocked_by": ["fingerprint_report"]}),

    # --- Red herring: Paul (motive present, opportunity blocked) ---
    ("paul_reed", "inheritance", "had-motive", {"unlocked_by": ["paul_motive_note"]}),
    ("paul_reed", "lounge", "seen-by", {"witness": "ray_webb", "time": "10:30 PM - 11:30 PM", "unlocked_by": ["card_game_witness"]}),

    # --- Red herring: Anna (motive present, opportunity blocked) ---
    ("anna_reed", "unhappy_marriage", "had-motive", {"unlocked_by": ["anna_motive_note"]}),
    ("anna_reed", "millbrook_station", "was-at", {"time": "10:30 PM", "unlocked_by": ["ticket_stamp"]}),

    # --- Red herring: Sam (suspicious clue, innocent) ---
    ("sam_fox", "engine_room", "was-at", {"time": "10:30 PM - 11:30 PM", "unlocked_by": ["repair_log"]}),
    ("sam_fox", "engine_room", "seen-by", {"witness": "mia_cole", "unlocked_by": ["repair_log"]}),
    ("sam_fox", "compartment_4", "seen-by", {"witness": "master_key_sign_out", "note": "he had the master key -- looks bad, but explained", "unlocked_by": ["master_key_log"]}),

    # --- Clues supporting the formal accusation slots ---
    ("money_report", "fear_of_arrest", "supports", {}),
    ("dining_log", "compartment_4", "supports", {}),
    ("fingerprint_report", "letter_opener", "supports", {}),

    # --- Statements ---
    ("anna_reed", "anna_alibi", "made-statement", {}),
    ("anna_alibi", "millbrook_station", "claims", {}),

    ("paul_reed", "paul_alibi", "made-statement", {}),
    ("paul_alibi", "lounge", "claims", {}),
    ("paul_alibi", "card_game_witness", "contradicts", {"decoy": True}),

    ("kate_lane", "kate_alibi", "made-statement", {}),
    ("kate_alibi", "dining_car", "claims", {}),
    ("kate_alibi", "dining_log", "contradicts", {"decoy": False}),

    ("sam_fox", "sam_alibi", "made-statement", {}),
    ("sam_alibi", "engine_room", "claims", {}),

    ("mia_cole", "mia_alibi", "made-statement", {}),
    ("mia_alibi", "lounge", "claims", {}),

    ("ray_webb", "webb_alibi", "made-statement", {}),
    ("webb_alibi", "lounge", "claims", {}),
]

# ---------------------------------------------------------------------------
# Briefing
# ---------------------------------------------------------------------------

BRIEFING_NODE_SLUGS = (
    ["jack_reed", "time_of_death", "unscheduled_stop"] + SUSPECTS + LOCATIONS
)

# ---------------------------------------------------------------------------
# Solution
# ---------------------------------------------------------------------------

SOLUTION = {
    "culprit": "kate_lane",
    "motive": {"clue": "money_report", "target": "fear_of_arrest", "relation": "had-motive"},
    "opportunity": {"clue": "dining_log", "target": "compartment_4", "relation": "was-at"},
    "means": {"clue": "fingerprint_report", "target": "letter_opener", "relation": "owned"},
}

# ---------------------------------------------------------------------------
# Confrontation reveals
# ---------------------------------------------------------------------------

CONFRONT_REVEALS = {
    "kate_alibi": {
        "reveal_edges": [("kate_lane", "compartment_4", "was-at")],
        "narration_hint": "Her story falls apart -- if she wasn't in the dining car, she was outside Jack's compartment when he died.",
    },
    "paul_alibi": {
        "reveal_edges": [],
        "narration_hint": "Paul sighs and admits he stepped out for a cigarette -- embarrassing, but not a crime.",
    },
}

# ---------------------------------------------------------------------------
# Interrogation topics
# ---------------------------------------------------------------------------

INTERROGATION_TOPICS = {
    "anna_reed": [
        {"id": "alibi", "label": "Where were you at 11 PM?", "statement": "anna_alibi", "reveals": []},
        {"id": "motive", "label": "How was your marriage?", "statement": None, "reveals": ["anna_motive_note"]},
    ],
    "paul_reed": [
        {"id": "alibi", "label": "Where were you at 11 PM?", "statement": "paul_alibi", "reveals": []},
        {"id": "motive", "label": "What do you get from Jack's will?", "statement": None, "reveals": ["paul_motive_note"]},
    ],
    "kate_lane": [
        {"id": "alibi", "label": "Where were you at 11 PM?", "statement": "kate_alibi", "reveals": []},
    ],
    "sam_fox": [
        {"id": "alibi", "label": "Where were you at 11 PM?", "statement": "sam_alibi", "reveals": []},
    ],
    "mia_cole": [
        {"id": "alibi", "label": "Where were you at 11 PM?", "statement": "mia_alibi", "reveals": []},
        {"id": "sam", "label": "Can you vouch for the train guard?", "statement": None, "reveals": ["repair_log"]},
    ],
    "ray_webb": [
        {"id": "alibi", "label": "Where were you at 11 PM?", "statement": "webb_alibi", "reveals": ["card_game_witness"]},
        {"id": "body", "label": "What did you find when you checked the body?", "statement": None, "reveals": ["fingerprint_report"]},
    ],
}
