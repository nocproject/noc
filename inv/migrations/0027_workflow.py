# ----------------------------------------------------------------------
# Set workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import bson

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("wf", "0001_default_wf")]

    def migrate(self):
        s_map = {
            1: bson.ObjectId("5a17f78d1bb6270001bd0346"),  # ALLOCATED -> Ready
            2: bson.ObjectId("5a17f7391bb6270001bd033e"),  # EXPIRED -> Cooldown
            3: bson.ObjectId("5a17f7d21bb6270001bd034f"),  # PLANNED -> Approved
            4: bson.ObjectId("5a17f6c51bb6270001bd0333"),  # RESERVED -> Reserved
            5: bson.ObjectId("5a17f7fc1bb6270001bd0359"),  # SUSPEND -> Suspended
        }
        db = self.mongo_db
        wf = bson.ObjectId("5a01d980b6f529000100d37a")  # Default Resource
        db["noc.interface_profiles"].update_many({}, {"$set": {"workflow": wf}})
        for s in s_map:
            db["noc.interfaces"].update_many({"state": s}, {"$set": {"state": s_map[s]}})
        # Missing state -> Ready
        state = bson.ObjectId("5a17f78d1bb6270001bd0346")
        db["noc.interfaces"].update_many({"state": {"$exists": False}}, {"$set": {"state": state}})
