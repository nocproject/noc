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
    layer = Layer.get_by_code("conduits")
    for oc in ObjectConnection.objects.filter(type="conduits"):
        oc.layer = layer
        oc.save()
