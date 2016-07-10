# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv log plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import InvPlugin


class LogPlugin(InvPlugin):
    name = "log"
    js = "NOC.inv.inv.plugins.log.LogPanel"

    def get_data(self, request, o):
        return {
            "id": str(o.id),
            "name": o.name,
            "model": o.model.name,
            "log": [
                {
                    "ts": x.ts.isoformat(),
                    "user": x.user,
                    "system": x.system,
                    "managed_object": x.managed_object,
                    "op": x.op,
                    "message": x.message
                }
                for x in o.get_log()
            ]
        }
