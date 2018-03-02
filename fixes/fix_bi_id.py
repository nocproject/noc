# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fill missed bi_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
# Third-party modules
from pymongo import UpdateOne
import bson
# NOC modules
from noc.models import get_model, is_document
from noc.core.bi.decorator import bi_hash

BI_SYNC_MODELS = [
    "ip.AddressProfile",
    "ip.PrefixProfile",
    "vc.VPNProfile"
]


def fix():
    for model_id in BI_SYNC_MODELS:
        model = get_model(model_id)
        print("[%s]" % model_id)
        if is_document(model):
            fix_document(model)
        else:
            fix_model(model)


def fix_document(model):
    coll = model._get_collection()
    bulk = []
    for d in coll.find({
        "bi_id": {
            "$exists": False
        }
    }, {
        "_id": 1
    }):
        bi_id = bi_hash(d["_id"])
        bulk += [
            UpdateOne({
                "_id": d["_id"]
            }, {
                "$set": {
                    "bi_id": bson.Int64(bi_id)
                }
            })
        ]
    if bulk:
        print("    Update %d items" % len(bulk))
        coll.bulk_write(bulk)


def fix_model(model):
    pass
