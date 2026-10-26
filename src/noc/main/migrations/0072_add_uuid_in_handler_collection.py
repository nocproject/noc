# ----------------------------------------------------------------------
# Add UUID in Handler collections
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import uuid

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        coll = self.mongo_db["handlers"]
        bulk_operations = []

        for p in coll.find({}):
            u = uuid.uuid4()
            query = {"_id": p["_id"], "$or": [{"uuid": {"$exists": False}}, {"uuid": ""}]}
            update_operation = UpdateOne(query, {"$set": {"uuid": u}})
            bulk_operations.append(update_operation)

        if bulk_operations:
            coll.bulk_write(bulk_operations)
