"""
Case registry. Each case module (case1, case2, case3) is a self-contained
truth graph: nodes, edges, statements, and a solution -- see any of them for
the shape. GraphStore.initialize(case_id) loads exactly one of these at a
time; switching cases wipes and reloads all three graphs from scratch.
"""

from backend.cases import case1, case2, case3

_MODULES = [case1, case2, case3]

CASES = {m.CASE_ID: m for m in _MODULES}

CASE_LIST = [
    {"id": m.CASE_ID, "title": m.CASE_TITLE, "blurb": m.CASE_BLURB}
    for m in _MODULES
]

DEFAULT_CASE_ID = case1.CASE_ID
