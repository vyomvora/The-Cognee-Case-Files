"""
Case #3 -- "Death at the Gallery".

Same shape as Cases #1 and #2 (six suspects, one killer, three red herrings,
one real lie, one decoy lie) but a different setting, cast, and clues.
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

CASE_ID = "case3"
CASE_TITLE = "Death at the Gallery"
CASE_BLURB = "An art gallery owner is killed in his office during his own party."

VICTIM_SLUG = "guy_marsh"
SCENE_SLUG = "office"
TIME_OF_DEATH = "10:00 PM"
SUMMARY = (
    "Guy Marsh, the owner of an art gallery, was found dead in his office at about 10:00 PM, "
    "during a party for his gallery's opening night. He was hit with something heavy. "
    "The fire alarm went off from 9:45 to 10:15 PM, and guests spilled out onto the street."
)

NODES = {}


def _add(cls, slug, **fields):
    node = cls(id=cls.id_for(f"{CASE_ID}:{slug}"), **fields)
    NODES[slug] = node
    return node


# --- Victim ---

_add(
    Victim,
    "guy_marsh",
    name="Guy Marsh",
    description="The owner of an art gallery. Found dead in his office, hit with something heavy.",
)

# --- Suspects ---

_add(
    Suspect,
    "rosa_marsh",
    name="Rosa Marsh",
    role="Daughter",
    description="Guy's daughter. Runs the gallery day to day.",
)
_add(
    Suspect,
    "leo_marsh",
    name="Leo Marsh",
    role="Son",
    description="Guy's son. Owes money to the wrong people, and was hoping Guy would help.",
)
_add(
    Suspect,
    "vince_cole",
    name="Vince Cole",
    role="Night Guard",
    description="Watches over the gallery at night. Carries a master key to every room.",
)
_add(
    Suspect,
    "elle_grant",
    name="Elle Grant",
    role="Art Dealer",
    description="A rival art dealer. She and Guy have argued for years over a painting.",
)
_add(
    Suspect,
    "ben_frost",
    name="Ben Frost",
    role="Assistant",
    description="Guy's assistant. Handles the gallery's paperwork and sales.",
)
_add(
    Suspect,
    "nora_diaz",
    name="Nora Diaz",
    role="Painter",
    description="A painter. Guy turned down her work for tonight's show, and she was upset about it.",
)

SUSPECTS = ["rosa_marsh", "leo_marsh", "vince_cole", "elle_grant", "ben_frost", "nora_diaz"]

# --- Locations ---

_add(Location, "office", name="The Office", description="Guy's office, just off the main gallery floor. A desk and a shelf of awards.")
_add(Location, "lobby", name="The Front Desk", description="Where guests sign in for the party. A guest book sits on the desk.")
_add(Location, "coat_check", name="The Coat Check", description="Where guests leave their coats. A small booth with a sign-out clock.")
_add(Location, "basement", name="The Basement", description="Where the building's fire alarm panel is kept.")
_add(Location, "bar", name="The Bar", description="Drinks and snacks for the party. A quiet corner away from the crowd.")
_add(Location, "supply_closet", name="The Supply Closet", description="A small room used to store cleaning supplies and spare uniforms.")
_add(Location, "gallery_entrance", name="The Gallery Entrance", description="The front door of the gallery, facing the street.")

LOCATIONS = ["office", "lobby", "coat_check", "basement", "bar", "supply_closet"]

# --- Weapon / Motive ---

_add(Weapon, "trophy", name="Bronze Trophy", description="A heavy bronze award trophy from Guy's office shelf.")

_add(Motive, "fear_of_exposure", name="Fear of Being Caught", description="Guy found out Ben had been selling fake copies of paintings. He planned to expose Ben and call the police that night.")
_add(Motive, "inheritance", name="Inheritance", description="Leo owes money to the wrong people. He was hoping for a large gift from Guy's will.")
_add(Motive, "old_rivalry", name="An Old Rivalry", description="Elle and Guy have argued for years over a painting she believes he stole from her.")

# --- Timeline events ---

_add(TimelineEvent, "time_of_death", name="Time of Death", time="10:00 PM", description="The doctor says Guy died at about 10:00 PM.")
_add(TimelineEvent, "fire_alarm", name="The Fire Alarm", time="9:45 PM - 10:15 PM", description="The fire alarm went off and guests rushed outside from 9:45 to 10:15 PM.")

# ---------------------------------------------------------------------------
# Clues
# ---------------------------------------------------------------------------

_add(Clue, "trophy_clue", name="A Missing Trophy", source_type="location", source_id="office",
     description="One bronze trophy is missing from the shelf in Guy's office. There's a clean mark where it used to sit.")
_add(Clue, "exposure_note", name="A Printed Email", source_type="location", source_id="office",
     description="A printed email on Guy's desk. It says he plans to expose someone for selling fake paintings and call the police tonight.")
_add(Clue, "signin_sheet", name="The Guest Sign-In Sheet", source_type="location", source_id="lobby",
     description="The guest book shows no one signed in after 9:30 PM. Whoever was supposed to be at the desk had stopped checking guests in.")
_add(Clue, "stained_jacket", name="A Stained Jacket", source_type="location", source_id="supply_closet",
     description="A jacket stuffed behind some boxes. It has dark stains on the sleeve, and Ben's name tag is sewn inside.")
_add(Clue, "bar_witness", name="Nora's Story", source_type="interrogation", source_id="nora_diaz",
     description="Nora says she was at the bar with Leo the whole night -- except for a few minutes when he slipped into the coat check room.")
_add(Clue, "coat_check_stub", name="A Coat Check Stub", source_type="location", source_id="coat_check",
     description="A stub stamped 9:40 PM, showing Elle picked up her coat and left before the fire alarm even went off.")
_add(Clue, "alarm_panel_log", name="An Alarm Panel Log", source_type="location", source_id="basement",
     description="A log shows Vince was resetting the alarm panel in the basement from 9:45 to 10:15 PM.")
_add(Clue, "master_key_log", name="Master Key Sign-Out", source_type="location", source_id="lobby",
     description="A sign-out sheet shows Vince had the master key tonight. Looks bad -- until you check where he actually was.")
_add(Clue, "leo_motive_note", name="Talk of Money Trouble", source_type="interrogation", source_id="leo_marsh",
     description="Leo admits he owes money to the wrong people, and was hoping Guy would help him tonight.")
_add(Clue, "elle_motive_note", name="Talk of the Old Argument", source_type="interrogation", source_id="elle_grant",
     description="Elle admits she and Guy have fought for years over a painting she believes he stole from her.")

CLUE_SLUGS = [
    "trophy_clue",
    "exposure_note",
    "signin_sheet",
    "stained_jacket",
    "bar_witness",
    "coat_check_stub",
    "alarm_panel_log",
    "master_key_log",
    "leo_motive_note",
    "elle_motive_note",
]

# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------

_add(Statement, "rosa_alibi", speaker="rosa_marsh", is_lie=False,
     name="Rosa's Story",
     text="I was in the basement with Vince, helping him reset the alarm panel.")
_add(Statement, "leo_alibi", speaker="leo_marsh", is_lie=True, decoy=True,
     name="Leo's Story",
     text="I never left the bar all night. Ask Nora, she was right there with me.")
_add(Statement, "vince_alibi", speaker="vince_cole", is_lie=False,
     name="Vince's Story",
     text="I was in the basement resetting the alarm panel. I was there the whole time it was going off.")
_add(Statement, "elle_alibi", speaker="elle_grant", is_lie=False,
     name="Elle's Story",
     text="I left before the alarm even went off. Ask at the coat check, they'll have the time.")
_add(Statement, "ben_alibi", speaker="ben_frost", is_lie=True,
     name="Ben's Story",
     text="I was at the front desk handing out drinks and checking in guests all night long.")
_add(Statement, "nora_alibi", speaker="nora_diaz", is_lie=False,
     name="Nora's Story",
     text="I was at the bar the whole time, same as Leo -- well, he did duck into the coat check room for a few minutes.")

STATEMENTS = {
    "rosa_marsh": "rosa_alibi",
    "leo_marsh": "leo_alibi",
    "vince_cole": "vince_alibi",
    "elle_grant": "elle_alibi",
    "ben_frost": "ben_alibi",
    "nora_diaz": "nora_alibi",
}

# ---------------------------------------------------------------------------
# Edges
# ---------------------------------------------------------------------------

EDGES = [
    # Public briefing facts.
    ("time_of_death", "office", "occurred-at", {"public": True}),
    ("guy_marsh", "office", "was-at", {"public": True}),
    ("fire_alarm", "office", "occurred-at", {"public": True}),

    # --- The solution chain (Ben Frost) ---
    ("ben_frost", "fear_of_exposure", "had-motive", {"unlocked_by": ["exposure_note"]}),
    ("ben_frost", "office", "was-at", {"time": "10:00 PM", "unlocked_by": ["signin_sheet"], "confront_only": True}),
    ("ben_frost", "trophy", "owned", {"unlocked_by": ["stained_jacket"]}),

    # --- Red herring: Leo (motive present, opportunity blocked) ---
    ("leo_marsh", "inheritance", "had-motive", {"unlocked_by": ["leo_motive_note"]}),
    ("leo_marsh", "bar", "seen-by", {"witness": "nora_diaz", "time": "9:30 PM - 10:30 PM", "unlocked_by": ["bar_witness"]}),

    # --- Red herring: Elle (motive present, opportunity blocked) ---
    ("elle_grant", "old_rivalry", "had-motive", {"unlocked_by": ["elle_motive_note"]}),
    ("elle_grant", "gallery_entrance", "was-at", {"time": "9:40 PM", "unlocked_by": ["coat_check_stub"]}),

    # --- Red herring: Vince (suspicious clue, innocent) ---
    ("vince_cole", "basement", "was-at", {"time": "9:45 PM - 10:15 PM", "unlocked_by": ["alarm_panel_log"]}),
    ("vince_cole", "basement", "seen-by", {"witness": "rosa_marsh", "unlocked_by": ["alarm_panel_log"]}),
    ("vince_cole", "office", "seen-by", {"witness": "master_key_sign_out", "note": "he had the master key -- looks bad, but explained", "unlocked_by": ["master_key_log"]}),

    # --- Clues supporting the formal accusation slots ---
    ("exposure_note", "fear_of_exposure", "supports", {}),
    ("signin_sheet", "office", "supports", {}),
    ("stained_jacket", "trophy", "supports", {}),

    # --- Statements ---
    ("rosa_marsh", "rosa_alibi", "made-statement", {}),
    ("rosa_alibi", "basement", "claims", {}),

    ("leo_marsh", "leo_alibi", "made-statement", {}),
    ("leo_alibi", "bar", "claims", {}),
    ("leo_alibi", "bar_witness", "contradicts", {"decoy": True}),

    ("vince_cole", "vince_alibi", "made-statement", {}),
    ("vince_alibi", "basement", "claims", {}),

    ("elle_grant", "elle_alibi", "made-statement", {}),
    ("elle_alibi", "gallery_entrance", "claims", {}),

    ("ben_frost", "ben_alibi", "made-statement", {}),
    ("ben_alibi", "lobby", "claims", {}),
    ("ben_alibi", "signin_sheet", "contradicts", {"decoy": False}),

    ("nora_diaz", "nora_alibi", "made-statement", {}),
    ("nora_alibi", "bar", "claims", {}),
]

# ---------------------------------------------------------------------------
# Briefing
# ---------------------------------------------------------------------------

BRIEFING_NODE_SLUGS = (
    ["guy_marsh", "time_of_death", "fire_alarm"] + SUSPECTS + LOCATIONS
)

# ---------------------------------------------------------------------------
# Solution
# ---------------------------------------------------------------------------

SOLUTION = {
    "culprit": "ben_frost",
    "motive": {"clue": "exposure_note", "target": "fear_of_exposure", "relation": "had-motive"},
    "opportunity": {"clue": "signin_sheet", "target": "office", "relation": "was-at"},
    "means": {"clue": "stained_jacket", "target": "trophy", "relation": "owned"},
}

# ---------------------------------------------------------------------------
# Confrontation reveals
# ---------------------------------------------------------------------------

CONFRONT_REVEALS = {
    "ben_alibi": {
        "reveal_edges": [("ben_frost", "office", "was-at")],
        "narration_hint": "Ben stops talking for a moment -- if he wasn't at the desk, he was in the office when Guy died.",
    },
    "leo_alibi": {
        "reveal_edges": [],
        "narration_hint": "Leo admits he stepped into the coat check room for a few minutes -- embarrassing, but not a crime.",
    },
}

# ---------------------------------------------------------------------------
# Interrogation topics
# ---------------------------------------------------------------------------

INTERROGATION_TOPICS = {
    "rosa_marsh": [
        {"id": "alibi", "label": "Where were you at 10 PM?", "statement": "rosa_alibi", "reveals": []},
        {"id": "vince", "label": "Can you vouch for Vince?", "statement": None, "reveals": ["alarm_panel_log"]},
    ],
    "leo_marsh": [
        {"id": "alibi", "label": "Where were you at 10 PM?", "statement": "leo_alibi", "reveals": []},
        {"id": "motive", "label": "What did you need from your father?", "statement": None, "reveals": ["leo_motive_note"]},
    ],
    "vince_cole": [
        {"id": "alibi", "label": "Where were you at 10 PM?", "statement": "vince_alibi", "reveals": []},
    ],
    "elle_grant": [
        {"id": "alibi", "label": "Where were you at 10 PM?", "statement": "elle_alibi", "reveals": []},
        {"id": "motive", "label": "What was your history with Guy?", "statement": None, "reveals": ["elle_motive_note"]},
    ],
    "ben_frost": [
        {"id": "alibi", "label": "Where were you at 10 PM?", "statement": "ben_alibi", "reveals": []},
    ],
    "nora_diaz": [
        {"id": "alibi", "label": "Where were you at 10 PM?", "statement": "nora_alibi", "reveals": ["bar_witness"]},
    ],
}
