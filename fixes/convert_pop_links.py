# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Convert legacy PoP links
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.gis.models.layer import Layer
# NOC modules
from noc.inv.models.objectconnection import ObjectConnection


def fix():
    for d in ObjectConnection._get_collection().find({"data.level": {"$exists": True}}):
        layer = Layer.get_by_code("pop_links%d" % (d["data"]["level"] // 10))
        oc = ObjectConnection.objects.filter(id=d["_id"]).first()
        oc.layer = layer
        oc.save()
