# ---------------------------------------------------------------------
# inv.inv inventory plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from .base import InvPlugin


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
            "model": o.model.get_short_label(),
        }
        # Navigation glyphs
        icon_cls = o.model.glyph_css_class
        if icon_cls:
            r["iconCls"] = icon_cls
        children = []
        nested_children = {c.parent_connection: c for c in o.iter_children()}
        for n in o.model.connections:
            if n.direction == "i":
                c = nested_children.get(n.name)
                if c is None:
                    children += [
                        {
                            "id": None,
                            "name": n.name,
                            "leaf": True,
                            "serial": None,
                            "description": "--- EMPTY ---",
                            "model": None,
                            "iconCls": "fa fa-square-o",
                        }
                    ]
                else:
                    cc = self.get_nested_inventory(c)
                    cc["name"] = n.name
                    children += [cc]
            elif n.direction == "s":
                children += [
                    {
                        "id": None,
                        "name": n.name,
                        "leaf": True,
                        "serial": None,
                        "description": n.description,
                        "model": ", ".join(str(p) for p in n.protocols),
                        "direction": "s",
                    }
                ]
        if children:
            # to_expand = "Transceiver" not in o.model.name
            to_expand = any(x for x in children if x.get("direction") != "s")
            r["children"] = children
            r["expanded"] = to_expand
        else:
            r["leaf"] = True
        return r

    def get_data(self, request, object):
        c = self.get_nested_inventory(object)
        c["name"] = object.model.description
        return {"expanded": True, "children": [c]}
