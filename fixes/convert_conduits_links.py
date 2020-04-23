# ---------------------------------------------------------------------
# Convert legacy PoP links
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.inv.models.objectconnection import ObjectConnection
from noc.gis.models.layer import Layer


def fix():
    layer = Layer.get_by_code("conduits")
    for oc in ObjectConnection.objects.filter(type="conduits"):
        oc.layer = layer
        oc.save()
