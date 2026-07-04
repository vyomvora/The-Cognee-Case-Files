"""
Node types for the Thornfield Manor truth graph.

Every node is a cognee DataPoint. IDs are derived deterministically from a
human-readable slug via ``Class.id_for(slug)`` so the rest of the codebase
can reference nodes by slug instead of juggling random UUIDs, while cognee
still gets a real, stable UUID identity for each node.
"""

from cognee.low_level import DataPoint


class Victim(DataPoint):
    name: str
    description: str
    metadata: dict = {"index_fields": ["name"]}


class Suspect(DataPoint):
    name: str
    role: str
    description: str
    metadata: dict = {"index_fields": ["name"]}


class Location(DataPoint):
    name: str
    description: str
    metadata: dict = {"index_fields": ["name"]}


class Weapon(DataPoint):
    name: str
    description: str
    metadata: dict = {"index_fields": ["name"]}


class Motive(DataPoint):
    name: str
    description: str
    metadata: dict = {"index_fields": ["name"]}


class TimelineEvent(DataPoint):
    name: str
    description: str
    time: str
    metadata: dict = {"index_fields": ["name"]}


class Clue(DataPoint):
    name: str
    description: str
    # "location" | "interrogation" -- where the player finds this clue.
    source_type: str
    # location slug or suspect slug matching source_type.
    source_id: str
    metadata: dict = {"index_fields": ["name"]}


class Statement(DataPoint):
    name: str
    text: str
    speaker: str  # suspect slug
    is_lie: bool
    metadata: dict = {"index_fields": ["text"]}


NODE_CLASSES = {
    "Victim": Victim,
    "Suspect": Suspect,
    "Location": Location,
    "Weapon": Weapon,
    "Motive": Motive,
    "TimelineEvent": TimelineEvent,
    "Clue": Clue,
    "Statement": Statement,
}
