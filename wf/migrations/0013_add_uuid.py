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
        coll = self.mongo_db["workflows"]
        for p in coll.find({}):
            u = uuid.uuid4()
            self.mongo_db["workflows"].update_one({"_id": p["_id"]}, {"$set": {"uuid": u}})

        coll = self.mongo_db["states"]
        for p in coll.find({}):
            u = uuid.uuid4()
            self.mongo_db["states"].update_one({"_id": p["_id"]}, {"$set": {"uuid": u}})

        coll = self.mongo_db["transitions"]
        for p in coll.find({}):
            u = uuid.uuid4()
            self.mongo_db["transitions"].update_one({"_id": p["_id"]}, {"$set": {"uuid": u}})

        coll = self.mongo_db["wfmigrations"]
        for p in coll.find({}):
            u = uuid.uuid4()
            self.mongo_db["wfmigrations"].update_one({"_id": p["_id"]}, {"$set": {"uuid": u}})
