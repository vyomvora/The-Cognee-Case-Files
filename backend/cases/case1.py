"""
Case #1 -- "A Death at Thornfield Manor".

Pure data: nodes, edges, statements, contradictions, and the solution chain.
graph_store.py loads this into cognee's truth graph when the player picks
this case; nothing here talks to cognee or the LLM directly.
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

CASE_ID = "case1"
CASE_TITLE = "A Death at Thornfield Manor"
CASE_BLURB = "A rich old man is killed in his own study during a storm. Six people were in the house."

VICTIM_SLUG = "edmund_thornfield"
SCENE_SLUG = "study"
TIME_OF_DEATH = "9:00 PM"
SUMMARY = (
    "Lord Edmund Thornfield was found dead in the Study at about 9:00 PM. He was hit with "
    "something heavy. Six people were in the house that night. The power went out from "
    "8:45 to 9:15 PM because of a storm."
)

# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

NODES = {}


def _add(cls, slug, **fields):
    node = cls(id=cls.id_for(f"{CASE_ID}:{slug}"), **fields)
    NODES[slug] = node
    return node


# --- Victim ---

_add(
    Victim,
    "edmund_thornfield",
    name="Lord Edmund Thornfield",
    description="The owner of Thornfield Manor. Found dead in the Study, hit with something heavy.",
)

# --- Suspects ---

_add(
    Suspect,
    "agnes_hale",
    name="Agnes Hale",
    role="Housekeeper",
    description="Has worked here for twenty years. Notices everything that happens in the house.",
)
_add(
    Suspect,
    "julian_thornfield",
    name="Julian Thornfield",
    role="Nephew",
    description="Edmund's nephew. Will inherit the estate now that Edmund is dead. Was drinking in the Billiard Room tonight.",
)
_add(
    Suspect,
    "silas_croft",
    name="Silas Croft",
    role="Family Doctor",
    description="The family doctor. Was a guest at dinner tonight. Careful and a bit full of himself.",
)
_add(
    Suspect,
    "eleanor_vance",
    name="Eleanor Vance",
    role="Secretary",
    description="Edmund's secretary. Handled his letters -- and, it turns out, his money too.",
)
_add(
    Suspect,
    "thomas_byrne",
    name="Thomas Byrne",
    role="Groundskeeper",
    description="Takes care of the garden and fixes things around the house. His boots are always muddy.",
)
_add(
    Suspect,
    "cordelia_thornfield",
    name="Cordelia Thornfield",
    role="Wife",
    description="Edmund's wife. They have been separated for a long time and are getting a divorce.",
)

SUSPECTS = [
    "agnes_hale",
    "julian_thornfield",
    "silas_croft",
    "eleanor_vance",
    "thomas_byrne",
    "cordelia_thornfield",
]

# --- Locations ---

_add(Location, "study", name="The Study", description="Where Lord Thornfield was found. A desk, a cold fireplace, and one candlestick missing from a pair.")
_add(Location, "library", name="The Library", description="Tall bookshelves and a basket for returned books. The door was locked from the outside during the blackout.")
_add(Location, "billiard_room", name="The Billiard Room", description="A pool table and the smell of brandy. Julian spent his evening here.")
_add(Location, "cellar", name="The Cellar", description="Cold and damp. The house's fuse box is down here -- it stopped working at 8:45.")
_add(Location, "hall", name="The Front Hall", description="Coats and umbrellas by the door. There's a small table where the mail is kept.")
_add(Location, "grounds", name="The Grounds", description="The garden outside. The ground is wet and muddy from the storm.")
_add(Location, "train_station", name="The Train Station", description="The small station near the manor.")

LOCATIONS = ["study", "library", "billiard_room", "cellar", "hall", "grounds"]

# --- Weapon / Motive ---

_add(Weapon, "brass_candlestick", name="Brass Candlestick", description="A heavy candlestick from the Study. It was part of a matching pair -- the other one is still on the shelf.")

_add(Motive, "fear_of_exposure", name="Fear of Being Caught", description="Edmund found out Eleanor had been stealing money from him. He planned to tell the police the next morning.")
_add(Motive, "inheritance", name="Inheritance", description="As Edmund's nephew, Julian gets the estate now that Edmund is dead.")
_add(Motive, "bitter_divorce", name="A Bad Divorce", description="Edmund and Cordelia were in the middle of an unpleasant divorce. He had recently removed her from his will.")

# --- Timeline events ---

_add(TimelineEvent, "time_of_death", name="Time of Death", time="9:00 PM", description="The doctor says Edmund died at about 9:00 PM.")
_add(TimelineEvent, "blackout", name="The Blackout", time="8:45 PM - 9:15 PM", description="A storm knocked out the power in the whole house from 8:45 to 9:15 PM.")

# ---------------------------------------------------------------------------
# Clues
# ---------------------------------------------------------------------------

_add(Clue, "brass_candlestick_clue", name="A Missing Candlestick", source_type="location", source_id="study",
     description="One candlestick from a matching pair is missing from the Study. The other one looks like it was handled roughly.")
_add(Clue, "embezzlement_ledger", name="A Hidden Notebook", source_type="location", source_id="study",
     description="A notebook hidden in the desk drawer. It's in Eleanor's handwriting, and it shows she has been quietly taking money from the estate for years.")
_add(Clue, "library_locked_stub", name="The Library Door", source_type="location", source_id="library",
     description="A note says the Library door was locked from the outside at 8:40 PM. It stayed locked through the whole blackout.")
_add(Clue, "bloodstained_gloves", name="Bloodstained Gloves", source_type="location", source_id="library",
     description="A pair of gloves with blood on them, hidden in the Library's return basket. Eleanor's name is stitched inside.")
_add(Clue, "train_ticket_stub", name="A Ticket Stub", source_type="location", source_id="hall",
     description="A train ticket for Mrs. C. Thornfield, timed 8:15 PM -- a full 45 minutes before the murder.")
_add(Clue, "fuse_box_note", name="A Note by the Fuse Box", source_type="location", source_id="cellar",
     description="A note pinned near the fuse box: 'Fixing this again -- T.B., about 8:40.' That matches the time the power went out.")
_add(Clue, "muddy_boots", name="Muddy Footprints", source_type="location", source_id="grounds",
     description="Fresh muddy footprints lead right up to the Study window. They look like they match Byrne's boots.")
_add(Clue, "billiard_witness", name="Dr. Croft's Story", source_type="interrogation", source_id="silas_croft",
     description="Dr. Croft says he was with Julian in the Billiard Room from 8:30 to 9:30 -- except for a few minutes around 9:05, when Julian stepped out to get a drink.")
_add(Clue, "julian_will_clause", name="Talk of the Will", source_type="interrogation", source_id="julian_thornfield",
     description="Julian admits, a little too quickly, that he will now get the whole estate.")
_add(Clue, "cordelia_divorce_papers", name="Divorce Papers", source_type="interrogation", source_id="cordelia_thornfield",
     description="Cordelia admits the divorce was unpleasant, and that Edmund had just removed her from his will.")

CLUE_SLUGS = [
    "brass_candlestick_clue",
    "embezzlement_ledger",
    "library_locked_stub",
    "bloodstained_gloves",
    "train_ticket_stub",
    "fuse_box_note",
    "muddy_boots",
    "billiard_witness",
    "julian_will_clause",
    "cordelia_divorce_papers",
]

# ---------------------------------------------------------------------------
# Statements (what each suspect says about 9 PM)
# ---------------------------------------------------------------------------

_add(Statement, "agnes_alibi", speaker="agnes_hale", is_lie=False,
     name="Agnes's Story",
     text="I was in the kitchen when the lights went out. Then I went straight down to help Thomas with the fuse box.")
_add(Statement, "julian_alibi", speaker="julian_thornfield", is_lie=True, decoy=True,
     name="Julian's Story",
     text="I never left the Billiard Room all night. Ask Dr. Croft -- he was with me the whole time.")
_add(Statement, "silas_alibi", speaker="silas_croft", is_lie=False,
     name="Dr. Croft's Story",
     text="Julian and I were in the Billiard Room from half past eight until well after nine. He did step out once, for a drink, around five past nine.")
_add(Statement, "eleanor_alibi", speaker="eleanor_vance", is_lie=True,
     name="Eleanor's Story",
     text="I was in the Library the whole time, from half past eight until they found the body. I never left it, not even once.")
_add(Statement, "thomas_alibi", speaker="thomas_byrne", is_lie=False,
     name="Thomas's Story",
     text="I was in the cellar the whole blackout, fixing that fuse box. Mrs. Hale came down and saw me there.")
_add(Statement, "cordelia_alibi", speaker="cordelia_thornfield", is_lie=False,
     name="Cordelia's Story",
     text="I left for the train station at a quarter past eight. I was on the 8:30 train long before anything happened.")

STATEMENTS = {
    "agnes_hale": "agnes_alibi",
    "julian_thornfield": "julian_alibi",
    "silas_croft": "silas_alibi",
    "eleanor_vance": "eleanor_alibi",
    "thomas_byrne": "thomas_alibi",
    "cordelia_thornfield": "cordelia_alibi",
}

# ---------------------------------------------------------------------------
# Edges: (source_slug, target_slug, relation, properties)
# ---------------------------------------------------------------------------

EDGES = [
    # Public briefing facts.
    ("time_of_death", "study", "occurred-at", {"public": True}),
    ("edmund_thornfield", "study", "was-at", {"public": True}),
    ("blackout", "study", "occurred-at", {"public": True}),

    # --- The solution chain (Eleanor Vance) ---
    ("eleanor_vance", "fear_of_exposure", "had-motive", {"unlocked_by": ["embezzlement_ledger"]}),
    ("eleanor_vance", "study", "was-at", {"time": "9:00 PM", "unlocked_by": ["library_locked_stub"], "confront_only": True}),
    ("eleanor_vance", "brass_candlestick", "owned", {"unlocked_by": ["bloodstained_gloves"]}),

    # --- Red herring: Julian (motive present, opportunity blocked) ---
    ("julian_thornfield", "inheritance", "had-motive", {"unlocked_by": ["julian_will_clause"]}),
    ("julian_thornfield", "billiard_room", "seen-by", {"witness": "silas_croft", "time": "8:30 PM - 9:30 PM", "unlocked_by": ["billiard_witness"]}),

    # --- Red herring: Cordelia (motive present, opportunity blocked) ---
    ("cordelia_thornfield", "bitter_divorce", "had-motive", {"unlocked_by": ["cordelia_divorce_papers"]}),
    ("cordelia_thornfield", "train_station", "was-at", {"time": "8:15 PM", "unlocked_by": ["train_ticket_stub"]}),

    # --- Red herring: Byrne (suspicious clue, innocent) ---
    ("thomas_byrne", "cellar", "was-at", {"time": "8:45 PM - 9:15 PM", "unlocked_by": ["fuse_box_note"]}),
    ("thomas_byrne", "cellar", "seen-by", {"witness": "agnes_hale", "unlocked_by": ["fuse_box_note"]}),
    ("thomas_byrne", "study", "seen-by", {"witness": "muddy_boots_trail", "note": "muddy footprints near the Study window -- looks bad, but explained", "unlocked_by": ["muddy_boots"]}),

    # --- Clues supporting the formal accusation slots (used by validation) ---
    ("embezzlement_ledger", "fear_of_exposure", "supports", {}),
    ("library_locked_stub", "study", "supports", {}),
    ("bloodstained_gloves", "brass_candlestick", "supports", {}),

    # --- Statements: who said them, what they claim, what breaks them ---
    ("agnes_hale", "agnes_alibi", "made-statement", {}),
    ("agnes_alibi", "cellar", "claims", {}),

    ("julian_thornfield", "julian_alibi", "made-statement", {}),
    ("julian_alibi", "billiard_room", "claims", {}),
    ("julian_alibi", "billiard_witness", "contradicts", {"decoy": True}),

    ("silas_croft", "silas_alibi", "made-statement", {}),
    ("silas_alibi", "billiard_room", "claims", {}),

    ("eleanor_vance", "eleanor_alibi", "made-statement", {}),
    ("eleanor_alibi", "library", "claims", {}),
    ("eleanor_alibi", "library_locked_stub", "contradicts", {"decoy": False}),

    ("thomas_byrne", "thomas_alibi", "made-statement", {}),
    ("thomas_alibi", "cellar", "claims", {}),

    ("cordelia_thornfield", "cordelia_alibi", "made-statement", {}),
    ("cordelia_alibi", "train_station", "claims", {}),
]

# ---------------------------------------------------------------------------
# Briefing: revealed to the player before any investigation begins.
# ---------------------------------------------------------------------------

BRIEFING_NODE_SLUGS = (
    ["edmund_thornfield", "time_of_death", "blackout"] + SUSPECTS + LOCATIONS
)

# ---------------------------------------------------------------------------
# The solution -- used only by validate_accusation(). The LLM never sees this.
# ---------------------------------------------------------------------------

SOLUTION = {
    "culprit": "eleanor_vance",
    "motive": {"clue": "embezzlement_ledger", "target": "fear_of_exposure", "relation": "had-motive"},
    "opportunity": {"clue": "library_locked_stub", "target": "study", "relation": "was-at"},
    "means": {"clue": "bloodstained_gloves", "target": "brass_candlestick", "relation": "owned"},
}

# ---------------------------------------------------------------------------
# What confronting a suspect over a caught contradiction reveals.
# ---------------------------------------------------------------------------

CONFRONT_REVEALS = {
    "eleanor_alibi": {
        "reveal_edges": [("eleanor_vance", "study", "was-at")],
        "narration_hint": "She stops making excuses -- if she wasn't in the Library, she was in the Study when the lights were out.",
    },
    "julian_alibi": {
        "reveal_edges": [],
        "narration_hint": "Julian turns red and admits he stepped out for a drink -- embarrassing, but not a crime.",
    },
}

# ---------------------------------------------------------------------------
# Interrogation topics offered to the player for each suspect.
# ---------------------------------------------------------------------------

INTERROGATION_TOPICS = {
    "agnes_hale": [
        {"id": "alibi", "label": "Where were you at 9 PM?", "statement": "agnes_alibi", "reveals": []},
        {"id": "byrne", "label": "Can you vouch for Thomas Byrne?", "statement": None, "reveals": ["fuse_box_note"]},
    ],
    "julian_thornfield": [
        {"id": "alibi", "label": "Where were you at 9 PM?", "statement": "julian_alibi", "reveals": []},
        {"id": "motive", "label": "What happens to the estate now?", "statement": None, "reveals": ["julian_will_clause"]},
    ],
    "silas_croft": [
        {"id": "alibi", "label": "Where were you at 9 PM?", "statement": "silas_alibi", "reveals": ["billiard_witness"]},
    ],
    "eleanor_vance": [
        {"id": "alibi", "label": "Where were you at 9 PM?", "statement": "eleanor_alibi", "reveals": []},
        {"id": "duties", "label": "What kind of work did you do for Lord Thornfield?", "statement": None, "reveals": []},
    ],
    "thomas_byrne": [
        {"id": "alibi", "label": "Where were you at 9 PM?", "statement": "thomas_alibi", "reveals": []},
        {"id": "boots", "label": "Why are your boots muddy by the Study window?", "statement": None, "reveals": []},
    ],
    "cordelia_thornfield": [
        {"id": "alibi", "label": "Where were you at 9 PM?", "statement": "cordelia_alibi", "reveals": []},
        {"id": "motive", "label": "How was your marriage?", "statement": None, "reveals": ["cordelia_divorce_papers"]},
    ],
}
