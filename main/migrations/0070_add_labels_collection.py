# ----------------------------------------------------------------------
# Migrate add uuid fild
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from pymongo import UpdateOne
from noc.core.migration.base import BaseMigration
import uuid

MONGO_CHUNK = 500


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["labels"]
        updates = []
        for d in coll.find({"uuid": {"$exists": False}}, {"_id": 1}):
            u = uuid.uuid4()
            updates += [UpdateOne({"_id": d["_id"]}, {"$set": {"uuid": u}})]
            if len(updates) >= MONGO_CHUNK:
                coll.bulk_write(updates)
                updates = []
        if updates:
            coll.bulk_write(updates)
