# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fix platform.full_name
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pymongo import UpdateOne
# NOC modules
from noc.lib.nosql import get_db


def fix():
    # Initialize with distinct values
    coll = get_db()["noc.platforms"]
    bulk = []
    for d in coll.find({
        "full_name": {
            "$exists": False
        }
    }, {"_id": 1}):
        bulk += [UpdateOne({
            "_id": d["_id"]
        }, {
            "$set": {"full_name": str(d["_id"])}
        })]
    if bulk:
        coll.bulk_write(bulk)
    fix_full_name()


def fix_full_name():
    from noc.inv.models.platform import Platform

    for p in Platform.objects.all():
        p.save()
