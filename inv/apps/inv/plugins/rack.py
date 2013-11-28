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
            )
        }
        return r
