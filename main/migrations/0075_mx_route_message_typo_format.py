# ----------------------------------------------------------------------
# Convert MessageType on MX Route
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne
from bson import Binary

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["messageroutes"]
        bulk = []

        for p in coll.find({}):
            if not p.get("type") or isinstance(p["type"], Binary):
                continue
            bulk.append(UpdateOne({"_id": p["_id"]}, {"$set": {"type": Binary(p["type"])}}))
        if bulk:
            coll.bulk_write(bulk)
