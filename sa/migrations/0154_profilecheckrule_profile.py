# ----------------------------------------------------------------------
# profilecheckrules
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
        pcrcoll = self.mongo_db["noc.profilecheckrules"]
        pmap = {}  # name -> id
        for d in pcoll.find({}, {"_id": 1, "name": 1}):
            pmap[d["name"]] = d["_id"]
        # Update
        for p in pmap:
            pcrcoll.update_many({"profile": p}, {"$set": {"profile": pmap[p]}})
