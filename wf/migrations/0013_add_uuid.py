# ----------------------------------------------------------------------
# Migrate add uuid fild
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration
import uuid


class Migration(BaseMigration):
    def migrate(self):
        for coll_name in ["workflows", "states", "transitions", "wfmigrations"]:
            coll = self.mongo_db[coll_name]
            for p in coll.find({}):
                u = uuid.uuid4()
                query = {"_id": p["_id"], "$or": [{"uuid": {"$exists": False}}, {"uuid": ""}]}
                self.mongo_db[coll_name].update_one(query, {"$set": {"uuid": u}})
