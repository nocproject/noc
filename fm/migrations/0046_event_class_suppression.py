# ----------------------------------------------------------------------
# Convert EventClass suppression rules
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Set

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        batch = []
        coll = self.mongo_db["noc.eventclasses"]
        coll.update_many({}, {"$set": {"suppression_window": 0}})
        for doc in coll.find(
            {"repeat_suppression": {"$exists": True}},
            {"_id": 1, "vars": 1, "repeat_suppression": 1},
        ):
            rs = doc.get("repeat_suppression") or None
            if not rs:
                continue
            # Get suppress vars key
            suppress_vars: Set[str] = set()
            for k in rs[0]["match_condition"]:
                if k.startswith("vars__"):
                    suppress_vars.add(k[6:])
            # Build bulk
            window = rs[0]["window"]
            vars = doc.get("vars") or []
            for v in vars:
                v["match_suppress"] = v["name"] in suppress_vars
            batch += [
                UpdateOne(
                    {"_id": doc["_id"]},
                    {
                        "$set": {"suppression_window": window, "vars": vars},
                        "$unset": {"repeat_suppression": ""},
                    },
                )
            ]
        if batch:
            coll.bulk_write(batch)
