# ----------------------------------------------------------------------
# Cleanup bad object_status documents
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import DeleteMany, InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        coll = self.mongo_db["noc.cache.object_status"]
        coll.delete_many({"object": {"$exists": False}})
        bulk = []
        for row in coll.aggregate(
            [
                {"$group": {"_id": "$object", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gte": 2}}},
            ]
        ):
            bulk += [DeleteMany({"object": row["_id"]})]
            r = coll.find_one({"object": row["_id"]})
            if r:
                bulk += [
                    InsertOne(
                        {
                            "object": r["object"],
                            "status": r.get("status", True),
                            "last": r.get("last"),
                        }
                    ),
                ]
        if bulk:
            coll.bulk_write(bulk, ordered=True)
