# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Areas overlay -
# Displays area bounds
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Areas overlay -
## Displays area bounds
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.gis.overlays.base import *
from noc.gis.models import Area


class AreasOverlay(OverlayHandler):
    def handle(self, **kwargs):
        r = {
            "type": "GeometryCollection",
            "geometries": []
        }

        for area in Area.objects.filter(is_active=True):
            r["geometries"] += [{
                "type": "Polygon",
                "coordinates": [[
                    area.SW,
                    [area.NE[0], area.SW[1]],
                    area.NE,
                    [area.SW[0], area.NE[1]],
                    area.SW
                ]]
            }]
        return r
