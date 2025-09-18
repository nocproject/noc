# ----------------------------------------------------------------------
# Convert Mongo binary fields named "uuid" to actual subtype (3 or 4).
# For Mongo connection with uuidRepresentation="standard" actual subtype is 4.
# For Mongo connection with uuidRepresentation="pythonLegacy" actual subtype is 3.
# See also: https://www.mongodb.com/docs/manual/reference/bson-types/#binary-data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Third-party modules
from bson.binary import Binary
from pymongo.collection import Collection as PM_Collection
from pymongo import UpdateOne

# NOC modules
from noc.core.collection.base import Collection
from noc.models import is_document


def fix():
    mongo_collections = (
        c
        for c in Collection.iter_collections()
        if is_document(c.model)
        # If you want to migrate only specific collections uncomment this
        # and specify them here.
        # (name is "json_collection" meta-field in model)
        #
        # and c.name in ["main.reports", "sa.actions", "sa.profiles"]
    )
    mongo_collections = sorted(mongo_collections, key=lambda c: c.name)
    print("Changed UUIDs in collection")
    print("---------------------------")
    scanned_colls = 0
    changed_colls = 0
    changed_uuids_sum = 0
    for c in mongo_collections:
        coll: PM_Collection = c.model._get_collection()
        print(f"{c.name}: ", end="")

        # For restore if collection has uuid_old (see below saving to uuid_old)
        #
        # restored_uuids = 0
        # for r in coll.find({"uuid": {"$exists": True}, "uuid_old": {"$exists": True}}):
        #     coll.update_one({"_id": r["_id"]}, {"$set": {"uuid": r["uuid_old"]}})
        #     #coll.update_one({"_id": r["_id"]}, {"$set": {"uuid": r["uuid_old"]}, "$unset": {"uuid_old": 1}})
        #     restored_uuids += 1
        # print("restored", restored_uuids)
        # continue

        changed_uuids = 0
        bulk = []
        for r in coll.find({"uuid": {"$exists": True}}):
            uuid = r["uuid"]
            if isinstance(uuid, Binary):
                uuid = uuid.as_uuid(uuid.subtype)
                # bulk += [UpdateOne({"_id": r["_id"]}, {"$set": {"uuid": uuid}})]
                bulk += [
                    UpdateOne({"_id": r["_id"]}, {"$set": {"uuid": uuid, "uuid_old": r["uuid"]}})
                ]
                changed_uuids += 1
        scanned_colls += 1
        if bulk:
            coll.bulk_write(bulk)
            changed_colls += 1
        print(changed_uuids)
        changed_uuids_sum += changed_uuids

    print("Summary")
    print("-------")
    print(f"Scanned collections: {scanned_colls}")
    print(f"Changed collections: {changed_colls}")
    print(f"Changed UUIDs: {changed_uuids_sum}")
