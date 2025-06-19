# ----------------------------------------------------------------------
# Remove duplicates by object from discoveryid
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from pymongo.collection import Collection

# NOC modules
from noc.inv.models.discoveryid import DiscoveryID


def fix():
    collection: Collection = DiscoveryID._get_collection()
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
    print(f"Found doubled by object documents: {len(ids_to_delete)}")
    if ids_to_delete:
        result = collection.delete_many({"_id": {"$in": ids_to_delete}})
        print(f"Removed documents: {result.deleted_count}")

    # rebuild index for `object` field
    idx_info = collection.index_information()
    for idx in idx_info:
        if tuple(k[0] for k in idx_info[idx]["key"]) == ("object",):
            collection.drop_index(idx)
            DiscoveryID.ensure_indexes()
            print(f"Index '{idx}' rebuilt")
            break
