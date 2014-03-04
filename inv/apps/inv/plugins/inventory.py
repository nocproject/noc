# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv inventory plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import InvPlugin


class InventoryPlugin(InvPlugin):
    name = "inventory"
    js = "NOC.inv.inv.plugins.inventory.InventoryPanel"

    def get_nested_inventory(self, o):
        rev = o.get_data("asset", "revision")
        if rev == "None":
            rev = ""
        r = {
            "id": str(o.id),
            "serial": o.get_data("asset", "serial"),
            "revision": rev or "",
            "description": o.model.description,
            "model": o.model.name
        }
        children = []
        for n in o.model.connections:
            if n.direction == "i":
                c, r_object, _ = o.get_p2p_connection(n.name)
                if c is None:
                    children += [{
                        "id": None,
                        "name": n.name,
                        "leaf": True,
                        "serial": None,
                        "description": "--- EMPTY ---",
                        "model": None
                    }]
                else:
                    cc = self.get_nested_inventory(r_object)
                    cc["name"] = n.name
                    children += [cc]
            elif n.direction == "s":
                children += [{
                    "id": None,
                    "name": n.name,
                    "leaf": True,
                    "serial": None,
                    "description": n.description,
                    "model": ", ".join(n.protocols)
                }]
        if children:
            to_expand = "Transceiver" not in o.model.name
            r["children"] = children
            r["expanded"] = to_expand
        else:
            r["leaf"] = True
        return r

    def get_data(self, request, object):
        c = self.get_nested_inventory(object)
        c["name"] = object.model.description
        return {
            "expanded": True,
            "children": [c]
        }
