# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fix inventory tree
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
#----------------------------------------------------------------------

## NOC modules
from noc.inv.models.discoveryid import DiscoveryID
from noc.core.mac import MAC

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
    if n:
        bulk.execute()
