# ----------------------------------------------------------------------
# inv.protocol application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.inv.models.protocol import Protocol
from noc.inv.models.modelinterface import ModelInterface
from noc.core.translation import ugettext as _


class ProtocolApplication(ExtDocApplication):
    """
    Protocol application
    """

    title = _("Protocol")
    menu = [_("Setup"), _("Protocols")]
    model = Protocol
    query_fields = ["code__icontains", "name__icontains", "description__icontains"]
    default_ordering = ["code"]

    def instance_to_dict(self, o: "Protocol", fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        # discriminator_interface, discriminator_attr, discriminators (code, value)
        if not r.get("discriminators"):
            return r
        discriminators = defaultdict(list)
        for item in o.discriminators:
            for d in item.data:
                discriminators[(d.interface, d.attr)] += [{"code": item.code, "value": d.value}]
        if not discriminators:
            return r
        (r["discriminator_interface"], r["discriminator_attr"]), r["discriminators"] = (
            discriminators.popitem()
        )
        mi = ModelInterface.get_by_name(r["discriminator_interface"])
        r["discriminator_interface"] = str(mi.id)
        r["discriminator_interface__label"] = mi.name
        return r

    def clean(self, data):
        discriminators = data.pop("discriminators", None)
        if not discriminators:
            return super().clean(data)
        interface, attr = data.pop("discriminator_interface", None), data.pop(
            "discriminator_attr", None
        )
        mi = ModelInterface.get_by_id(interface)
        attr = mi.get_attr(attr)
        data["discriminators"] = []
        for d in discriminators:
            value = attr._clean(d["value"])
            data["discriminators"] += [
                {
                    "data": [{"interface": mi.name, "attr": attr.name, "value": value}],
                    "code": d["code"],
                }
            ]
        # Clean other
        return super().clean(data)

    @view(url="^lookup_tree/", method=["GET"], access=True)
    def api_protocols_lookup_tree(self, request):
        r = {}
        protocol_filter = {}
        query = request.GET.get("__query")
        if query:
            protocol_filter["name__icontains"] = query
        for p in Protocol.objects.filter(**protocol_filter).order_by("technology", "code"):
            if p.technology.name not in r:
                r[p.technology.name] = defaultdict(list)
            for v in p.iter_protocol_variants():
                r[p.technology.name][p.name].append(
                    {
                        "name": v.code,
                        # "type": f.type,
                        "parent": p.name,
                        "id": str(v.code),
                        "leaf": True,
                        "is_protected": False,
                        "scope": f"{p.code}::{v.discriminator or ''}",
                        "value": v.direction,
                        "badges": ["fa-ils"],
                        "bg_color1": "#ffffff",
                        "fg_color1": "#ffffff",
                        "bg_color2": "#000000",
                        "fg_color2": "#000000",
                        # "checked": False,
                    }
                )
        leafs = defaultdict(list)
        for t, i1 in r.items():
            for p, i2 in i1.items():
                leafs[t] += [{"name": p, "leaf": False, "is_protected": False, "children": i2}]
        return self.render_json(
            {
                "name": "root",
                "is_protected": False,
                "leaf": False,
                "children": [
                    {"name": lf, "leaf": False, "is_protected": False, "children": leafs[lf]}
                    for lf in leafs
                ],
            }
        )
