# ----------------------------------------------------------------------
# Add UUID in Handler collections
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
from pymongo import UpdateOne
import uuid


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["handlers"]
        bulk_operations = []

        for p in coll.find({}):
            u = uuid.uuid4()
            query = {"_id": p["_id"], "$or": [{"uuid": {"$exists": False}}, {"uuid": ""}]}
            update_operation = UpdateOne(query, {"$set": {"uuid": u}})
            bulk_operations.append(update_operation)

        if bulk_operations:
            coll.bulk_write(bulk_operations)
