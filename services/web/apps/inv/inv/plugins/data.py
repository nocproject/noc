# ---------------------------------------------------------------------
# inv.inv data plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, Tuple, List, Optional
from collections import defaultdict

# NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.modelinterface import ModelInterface
from noc.sa.interfaces.base import StringParameter, UnicodeParameter
from .base import InvPlugin


class DataPlugin(InvPlugin):
    name = "data"
    js = "NOC.inv.inv.plugins.data.DataPanel"

    RGROUPS = [
        [
            "Building",
            "PoP | International",
            "PoP | National",
            "PoP | Regional",
            "PoP | Core",
            "PoP | Aggregation",
            "PoP | Access",
        ]
    ]

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            "api_plugin_%s_save_data" % self.name,
            self.api_save_data,
            url="^(?P<id>[0-9a-f]{24})/plugin/data/$",
            method=["PUT"],
            validate={
                "interface": StringParameter(),
                "key": StringParameter(),
                "value": UnicodeParameter(),
            },
        )

    def get_data(self, request, o: Object):
        data = []
        common = [
            ("Name", " | ".join(o.get_name_path()), "Inventory name", False),
            ("Vendor", o.model.vendor.name, "Hardware vendor", True),
            ("Model", o.model.name, "Inventory model", True),
            ("ID", str(o.id), "Internal ID", True),
        ]
        if o.remote_system:
            common += [
                ("Remote System", o.remote_system.name, "Remote System Name", True),
                ("RemoteID", o.remote_id, "Remote System ID", True),
            ]
        for k, v, d, is_const in common:
            r = {
                "interface": "Common",
                "name": k,
                "value": v,
                "type": "str",
                "description": d,
                "required": True,
                "is_const": is_const,
                "choices": None,
                "scope": "",
            }
            if k == "Model":
                for rg in self.RGROUPS:
                    if v in rg:
                        # Model can be changed
                        r["is_const"] = False
                        g = [ObjectModel.objects.get(name=x) for x in rg]
                        r["choices"] = [[str(x.id), x.name] for x in g]
                        break
            data += [r]
        # Build result
        mi_values: Dict[str, Dict[str, List[Tuple[Optional[str], str]]]] = {}
        for item in o.get_effective_data():
            if item.interface not in mi_values:
                mi_values[item.interface] = defaultdict(list)
            mi_values[item.interface][item.attr] += [(item.value, item.scope)]
        for i in mi_values:
            mi = ModelInterface.get_by_name(i)
            if not mi:
                continue
            for a in mi.attrs:
                for value, scope in mi_values[i].get(a.name, [(None, "")]):
                    if value is None and a.is_const:
                        continue
                    data += [
                        {
                            "interface": i,
                            "name": a.name,
                            "scope": scope,
                            "value": value,
                            "type": a.type,
                            "description": a.description,
                            "required": a.required,
                            "is_const": a.is_const,
                        }
                    ]
        return {"id": str(o.id), "name": o.name, "model": o.model.name, "data": data}

    def api_save_data(self, request, id, interface=None, key=None, value=None):
        o = self.app.get_object_or_404(Object, id=id)
        if interface == "Common":
            # Fake interface
            if key == "Name":
                o.name = value.split("|")[-1].strip()
            elif key == "Model":
                m = self.app.get_object_or_404(ObjectModel, id=value)
                o.model = m
                o.log(message="Changing model to %s" % m.name, user=request.user, system="WEB")
                o.save()
        else:
            if value is None or value == "":
                o.reset_data(interface, key)
            else:
                o.set_data(interface, key, value)
        o.save()
