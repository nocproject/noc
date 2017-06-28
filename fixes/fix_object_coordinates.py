# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Set object coordinates according to data
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.object import Object


def fix():
    for d in Object._get_collection().find({
        "data.geopoint.x": {
            "$exists": True
        }
    }, {
        "_id": 1
    }):
        o = Object.get_by_id(d["_id"])
        o.save()
