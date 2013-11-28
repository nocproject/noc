# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv data plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import InvPlugin
from noc.inv.models.modelinterface import ModelInterface
from noc.lib.utils import deep_merge


class DataPlugin(InvPlugin):
    name = "data"
    js = "NOC.inv.inv.plugins.data.DataPanel"

    def get_data(self, request, o):
        data = []
        for k, v, d in [
                ("Name", " | ".join(o.get_name_path()), "Inventory name"),
                ("Vendor", o.model.vendor.name, "Hardware vendor"),
                ("Model", o.model.name, "Inventory model"),
                ("ID", str(o.id), "Internal ID")
            ]:
            data += [{
                "interface": "Common",
                "name": k,
                "value": v,
                "type": "str",
                "description": d,
                "required": True,
                "is_const": True
            }]
        d = deep_merge(o.model.data, o.data)
        for i in d:
            mi = ModelInterface.objects.filter(name=i).first()
            if not mi:
                continue
            for k in d[i]:
                a = mi.get_attr(k)
                if not a:
                    continue
                data += [{
                    "interface": i,
                    "name": k,
                    "value": d[i][k],
                    "type": a.type,
                    "description": a.description,
                    "required": a.required,
                    "is_const": a.is_const
                }]
        return {
            "name": o.name,
            "model": o.model.name,
            "data": data,
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
