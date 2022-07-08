# ----------------------------------------------------------------------
# Initialize bi_id field
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne
import bson

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.bi.decorator import bi_hash

MONGO_CHUNK = 500


class Migration(BaseMigration):
    def migrate(self):
        # Update mongodb collections
        for coll_name in ["noc.addresses", "noc.divisions", "noc.streets"]:
            coll = self.mongo_db[coll_name]
            updates = []
            for d in coll.find({"bi_id": {"$exists": False}}, {"_id": 1}):
                updates += [
                    UpdateOne(
                        {"_id": d["_id"]},
                        {"$set": {"bi_id": bson.Int64(bi_hash(d["_id"]))}},
                    )
                ]
                if len(updates) >= MONGO_CHUNK:
                    coll.bulk_write(updates)
                    updates = []
            if updates:
                coll.bulk_write(updates)
