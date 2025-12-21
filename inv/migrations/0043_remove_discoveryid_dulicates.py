# ----------------------------------------------------------------------
# Remove DiscoveryID Duplicated indexes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        collection = self.mongo_db["noc.inv.discovery_id"]
        objects = collection.aggregate(
            [
                {"$group": {"_id": "$object", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}},
                {"$match": {"count": {"$gt": 1}}},
            ],
            allowDiskUse=True,
        )
        ids_to_delete = []
        for o in objects:
            ids_to_delete += o["ids"][1:]
        if ids_to_delete:
            collection.delete_many({"_id": {"$in": ids_to_delete}})
        # rebuild index for `object` field
        idx_info = collection.index_information()
        for idx in idx_info:
            if tuple(k[0] for k in idx_info[idx]["key"]) == ("object",):
                collection.drop_index(idx)
                break
