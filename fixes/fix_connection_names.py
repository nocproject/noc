# ----------------------------------------------------------------------
# Fix mododel connection names
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Tuple, List, Any, DefaultDict, Optional
from collections import defaultdict

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.text import str_distance
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection


def fix():
    def find_nearest(x: str, items: List[str]) -> Optional[str]:
        best: Optional[str] = None
        best_dist: Optional[int] = None

        for i in items:
            d = str_distance(x, i)
            if best_dist is None or d < best_dist:
                best_dist = d
                best = i
        return best

    # Get connection directions
    conn_dirs: Dict[Tuple[ObjectId, str], str] = {}
    for doc in ObjectModel._get_collection().find({}, {"_id": 1, "connections": 1}):
        conns: List[Dict[str, Any]] = doc.get("connections")
        if not conns:
            continue
        for c in conns:
            conn_dirs[doc["_id"], c["name"]] = c["direction"]
    mod_conns: DefaultDict[ObjectId, List] = defaultdict(list)
    for m, n in conn_dirs:
        mod_conns[m].append(n)
    # Get object models
    obj_models: Dict[ObjectId, ObjectId] = {
        doc["_id"]: doc["model"]
        for doc in Object._get_collection().find({}, {"_id": 1, "model": 1})
    }
    # Validate object connections
    for doc in ObjectConnection._get_collection().find({}):
        conns = doc.get("connection")
        if not conns:
            continue
        for c in conns:
            model = obj_models.get(c["object"])
            if not model:
                print(f"Hanging connection {doc['id']}. Missed object {c['object']}")
                continue
            cn = c["name"]
            if (model, cn) not in conn_dirs:
                # Renamed or deleted connection
                nearest = find_nearest(cn, mod_conns[model])
                print(f"Renaming connection connection `{cn}` -> `{nearest}`")
