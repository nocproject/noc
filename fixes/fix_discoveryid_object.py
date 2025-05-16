# ----------------------------------------------------------------------
# Remove duplicates by object from discoveryid
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import DeleteOne

# NOC modules
from noc.inv.models.discoveryid import DiscoveryID


def fix():
    collection = DiscoveryID._get_collection()
    objects = collection.aggregate(
        [
            {"$group": {"_id": "$object", "count": {"$sum": 1}, "ids": {"$push": "$_id"}}},
            {"$match": {"count": {"$gt": 1}}},
        ],
        allowDiskUse=True,
    )
    bulk = []
    dbl_counter = 0
    for o in objects:
        ids: list = o["ids"][1:]
        for _id in ids:
            bulk += [DeleteOne({"_id": _id})]
            dbl_counter += 1
    print(f"Found doubled by object documents: {dbl_counter}")
    if bulk:
        try:
            collection.bulk_write(bulk)
            print(f"Removed documents: {dbl_counter}")
        except BulkWriteError as e:
            print("Bulk write error: '%s'", e.details)

    # rebuild index for `object` field
    idx_info = collection.index_information()
    for idx in idx_info:
        if tuple(k[0] for k in idx_info[idx]["key"]) == ("object",):
            collection.drop_index(idx)
            DiscoveryID.ensure_indexes()
            print(f"Index '{idx}' rebuilt")
            break
