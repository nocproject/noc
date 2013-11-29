# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv data plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import InvPlugin


class RackPlugin(InvPlugin):
    name = "rack"
    js = "NOC.inv.inv.plugins.rack.RackPanel"

    def get_data(self, request, o):
        r = {
            "rack": dict(
                (k, o.get_data("rack", k))
                for k in ("units", "width", "depth")
            ),
            "content": []
        }
        for c in o.get_content():
            units = c.get_data("rackmount", "units")
            pos = c.get_data("rackmount", "position")
            side = c.get_data("rackmount", "side") or "f"
            if units and pos:
                r["content"] += [{
                    "units": units,
                    "pos": pos,
                    "name": c.name,
                    "side": side
                }]
        return r
