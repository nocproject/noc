# ----------------------------------------------------------------------
# Fill Active/ArchivedAlarm managed object profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-party modules
from pymongo import UpdateMany

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm


BULK_SIZE = 50
IN_SIZE = 1000


def fix():
    def fix_model(model):
        coll = model._get_collection()
        ins = defaultdict(list)
        bulk = []
        for doc in coll.find(
            {"managed_object_profile": {"$exists": False}, "managed_object": {"$exists": True}},
            {"_id": 1, "managed_object": 1},
        ):
            mo = ManagedObject.get_by_id(doc["managed_object"])
            if not mo:
                continue
            mop = mo.object_profile.id
            ins[mop] += [doc["_id"]]
            if len(ins[mop]) >= IN_SIZE:
                bulk += [
                    UpdateMany(
                        {"_id": {"$in": ins[mop]}}, {"$set": {"managed_object_profile": mop}}
                    )
                ]
                ins[mop] = []
                if len(bulk) >= BULK_SIZE:
                    coll.bulk_write(bulk)
                    bulk = []
        if bulk:
            coll.bulk_write(bulk)

    fix_model(ActiveAlarm)
    fix_model(ArchivedAlarm)
