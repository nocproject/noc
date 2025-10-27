# ----------------------------------------------------------------------
# Add Vars mapping to Event Disposition Rule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["dispositionrules"]
        coll.update_many(
            {"vars_conditions": {"$exists": True}},
            {"$rename": {"vars_conditions": "vars_op"}},
        )
        bulk = []
        for d in coll.find({"vars_op.field": {"$exists": True}}):
            for v in d["vars_op"]:
                v["name"] = v.pop("field")
            bulk.append(UpdateOne({"_id": d["_id"]}, {"$set": {"vars_op": d["vars_op"]}}))
        if bulk:
            coll.bulk_write(bulk)
        # Send Update datastream
