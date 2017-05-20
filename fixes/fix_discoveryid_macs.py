# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fix MAC index
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
#----------------------------------------------------------------------

## NOC modules
from noc.inv.models.discoveryid import DiscoveryID
from noc.core.mac import MAC

BATCH_SIZE = 10000


def fix():
    collection = DiscoveryID._get_collection()
    bulk = collection.initialize_unordered_bulk_op()
    n = 0
    for d in DiscoveryID._get_collection().find():
        ranges = d.get("chassis_mac", [])
        if not ranges:
            continue
        macs = []
        for r in ranges:
            first = MAC(r["first_mac"])
            last = MAC(r["last_mac"])
            macs += [m for m in range(int(first), int(last) + 1)]
        bulk.find({"_id": d["_id"]}).update({
            "$set": {
                "macs": macs
            }
        })
        n += 1
        if n == BATCH_SIZE:
            bulk.execute()
            n = 0
            bulk = collection.initialize_unordered_bulk_op()
    if n:
        bulk.execute()
