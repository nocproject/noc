# ----------------------------------------------------------------------
# Fix MAC index
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
# Third-party modules
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne

# NOC modules
from noc.inv.models.discoveryid import DiscoveryID
from noc.core.mac import MAC

BATCH_SIZE = 10000


def fix():
    collection = DiscoveryID._get_collection()
    bulk = []
    for d in DiscoveryID._get_collection().find():
        ranges = d.get("chassis_mac", [])
        if not ranges:
            continue
        macs = []
        for r in ranges:
            first = MAC(r["first_mac"])
            last = MAC(r["last_mac"])
            macs += list(range(int(first), int(last) + 1))
        bulk += [UpdateOne({"_id": d["_id"]}, {"$set": {"macs": macs}})]
        if len(bulk) == BATCH_SIZE:
            print("Commiting changes to database")
            try:
                collection.bulk_write(bulk)
                bulk = []
                print("Database has been synced")
            except BulkWriteError as e:
                print("Bulk write error: '%s'", e.details)
                print("Stopping check")
                bulk = []
    if bulk:
        collection.bulk_write(bulk)
