# ----------------------------------------------------------------------
# Fill missed bi_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne
import bson

# NOC modules
from noc.core.bi.decorator import bi_hash
from noc.core.mongo.connection import get_db

BI_COLLECTIONS = [
    "addressprofiles",
    "prefixprofiles",
    "vpnprofiles",
    "noc.firmwares",
    "noc.platforms",
    "noc.vendors",
    "technologies",
    "noc.profiles",
]


def fix():
    db = get_db()
    for coll_name in BI_COLLECTIONS:
        print(f"[{coll_name}]")
        coll = db[coll_name]
        bulk = []
        for d in coll.find({"bi_id": {"$exists": False}}, {"_id": 1}):
            bi_id = bi_hash(d["_id"])
            bulk.append(UpdateOne({"_id": d["_id"]}, {"$set": {"bi_id": bson.Int64(bi_id)}}))
        if bulk:
            print(f"    Update {len(bulk)} items")
            coll.bulk_write(bulk)
