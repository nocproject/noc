# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv data plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import InvPlugin
from noc.inv.models.object import Object
from noc.inv.models.modelinterface import ModelInterface
from noc.lib.utils import deep_merge
from noc.sa.interfaces.base import StringParameter, UnicodeParameter


class DataPlugin(InvPlugin):
    name = "data"
    js = "NOC.inv.inv.plugins.data.DataPanel"

    def init_plugin(self):
        super(DataPlugin, self).init_plugin()
        self.add_view(
            "api_plugin_%s_save_data" % self.name,
            self.api_save_data,
            url="^(?P<id>[0-9a-f]{24})/plugin/data/$",
            method=["PUT"],
            validate={
                "interface": StringParameter(),
                "key": StringParameter(),
                "value": UnicodeParameter()
            }
        )

    def get_data(self, request, o):
        data = []
        for k, v, d, is_const in [
                ("Name", " | ".join(o.get_name_path()), "Inventory name", False),
                ("Vendor", o.model.vendor.name, "Hardware vendor", True),
                ("Model", o.model.name, "Inventory model", True),
                ("ID", str(o.id), "Internal ID", True)
            ]:
            data += [{
                "interface": "Common",
                "name": k,
                "value": v,
                "type": "str",
                "description": d,
                "required": True,
                "is_const": is_const
            }]
        d = deep_merge(o.model.data, o.data)
        for i in d:
            mi = ModelInterface.objects.filter(name=i).first()
            if not mi:
                continue
            for a in mi.attrs:
                v = d[i].get(a.name)
                if v is None and a.is_const:
                    continue
                data += [{
                    "interface": i,
                    "name": a.name,
                    "value": v,
                    "type": a.type,
                    "description": a.description,
                    "required": a.required,
                    "is_const": a.is_const
                }]
        return {
            "id": str(o.id),
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

    def api_save_data(self, request, id,
                 interface=None, key=None, value=None):
        o = self.app.get_object_or_404(Object, id=id)
        if interface == "Common":
            # Fake interface
            if key == "Name":
                o.name = value.split("|")[-1].strip()
        else:
            if value is None or value == "":
                o.reset_data(interface, key)
            else:
                o.set_data(interface, key, value)
        o.save()
