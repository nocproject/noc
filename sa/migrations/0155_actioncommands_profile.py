# ----------------------------------------------------------------------
# actioncommands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Get profile record mappings
        pcoll = self.mongo_db["noc.profiles"]
        acoll = self.mongo_db["noc.actioncommands"]
        pmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "name": 1}):
            pmap[d["name"]] = d["_id"]
        # Update
        for p in pmap:
            acoll.update_many({"profile": p}, {"$set": {"profile": pmap[p]}})
