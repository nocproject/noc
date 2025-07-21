# ----------------------------------------------------------------------
# Convert Notification Group Watch to alarm
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
        bulk = []
        coll = self.mongo_db["noc.alarms.active"]
        for aa in coll.find({"watchers": {"$exists": True}}, {"watchers": 1}):
            watchers = []
            for w in aa.get("watchers", []):
                w["key"] = str(w["key"])
                watchers.append(w)
            if watchers:
                bulk += [UpdateOne({"_id": aa["_id"]}, {"$set": {"watchers": watchers}})]
        if bulk:
            coll.bulk_write(bulk)
