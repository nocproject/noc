# ----------------------------------------------------------------------
# Clean CPE.caps scope
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

# Third-party modules
from pymongo import UpdateOne


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        # Migrate profiles
        cpe_coll = db["cpes"]
        bulk = []
        # DropIndex
        for cpe in cpe_coll.find({"caps": {"$exists": True}}, {"caps": 1}):
            caps = []
            for c in cpe.get("caps") or []:
                if c.get("scope") == "cpe":
                    c.pop("scope", None)
                    c["source"] = "discovery"
                else:
                    c["source"] = "database"
                caps.append(c)
            if caps:
                bulk += [
                    UpdateOne({"_id": cpe["_id"]}, {"$set": {"caps": caps}}),
                ]
            if len(bulk) > 500:
                cpe_coll.bulk_write(bulk)
                bulk = []
        if bulk:
            cpe_coll.bulk_write(bulk)
