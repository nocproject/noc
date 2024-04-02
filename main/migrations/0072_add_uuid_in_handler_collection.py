# ----------------------------------------------------------------------
# Add UUID in Handler collections
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
import uuid


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["handlers"]
        for p in coll.find({}):
            u = uuid.uuid4()
            query = {"_id": p["_id"], "$or": [{"uuid": {"$exists": False}}, {"uuid": ""}]}
            self.mongo_db["handlers"].update_one(query, {"$set": {"uuid": u}})
