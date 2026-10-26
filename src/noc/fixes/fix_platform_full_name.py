# ----------------------------------------------------------------------
# Fix platform.full_name
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import UpdateOne

# NOC modules
from noc.core.mongo.connection import get_db


def fix():
    # Initialize with distinct values
    coll = get_db()["noc.platforms"]
    bulk = []
    for d in coll.find({"full_name": {"$exists": False}}, {"_id": 1}):
        bulk.append(UpdateOne({"_id": d["_id"]}, {"$set": {"full_name": str(d["_id"])}}))
    if bulk:
        coll.bulk_write(bulk)
    fix_full_name()


def fix_full_name():
    # NOC modules
    from noc.inv.models.platform import Platform

    for p in Platform.objects.all():
        p.save()
