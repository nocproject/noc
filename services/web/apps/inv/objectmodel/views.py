# ---------------------------------------------------------------------
# inv.objectmodel application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-party modules
from mongoengine.queryset import Q

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.main.models.doccategory import DocCategory
from noc.inv.models.objectmodel import ObjectModel, ProtocolVariantItem
from noc.inv.models.modelinterface import ModelInterface
from noc.inv.models.protocol import ProtocolVariant
from noc.sa.interfaces.base import ListOfParameter, DocumentParameter
from noc.core.prettyjson import to_json
from noc.core.translation import ugettext as _


class ObjectModelApplication(ExtDocApplication):
    """
    ObjectModel application
    """

    title = _("Object Models")
    menu = [_("Setup"), _("Object Models")]
    model = ObjectModel
    parent_model = DocCategory
    parent_field = "parent"
    query_fields = [
        "name__icontains",
        "description__icontains",
        "uuid",
    ]

    def get_Q(self, request, query):
        q = super().get_Q(request, query)
        q |= Q(
            data__match={
                "interface": "asset",
                "attr__in": ["part_no", "order_part_no"],
                "value": query,
            }
        )
        return q

    def instance_to_dict(self, o, fields=None, nocustom=False):
        if isinstance(o, ProtocolVariantItem):
            return str(o)
        r = super().instance_to_dict(o, fields, nocustom=nocustom)
        if isinstance(o, ObjectModel) and "connections" in r:
            for c in r["connections"]:
                data = c.pop("data", None)
                for d in data or []:
                    d["connection"] = c["name"]
                    r["data"].append(d)
        return r

    def clean(self, data):
        model_data = []
        connection_data = defaultdict(list)
        for d in data.get("data", []):
            c = d.pop("connection", None)
            if c:
                connection_data[c].append(d)
            else:
                model_data.append(d)
        print("connection data", connection_data)
        if model_data:
            data["data"] = ModelInterface.clean_data(model_data)
        if "data" in data:
            data["data"] = ModelInterface.clean_data(data["data"])
        if "plugins" in data and data["plugins"]:
            data["plugins"] = [x.strip() for x in data["plugins"].split(",") if x.strip()]
        else:
            data["plugins"] = None
        if "connections" not in data:
            return super().clean(data)
        for c in data["connections"]:
            if connection_data and c["name"] in connection_data:
                c["data"] = ModelInterface.clean_data(connection_data[c["name"]])
            if "protocols" not in c:
                continue
            protocols = []
            for p in c.get("protocols") or []:
                p = ProtocolVariant.get_by_code(p)
                protocols += [{"protocol": p.protocol.id, "direction": p.direction}]
                if p.discriminator:
                    protocols[-1]["discriminator"] = p.discriminator
            c["protocols"] = protocols
        print("D", data)
        return super().clean(data)

    def cleaned_query(self, q):
        if "is_container" in q:
            q["data__container__container"] = True
            q["name__ne"] = "Root"
            del q["is_container"]
        return super().cleaned_query(q)

    @view(url="^(?P<id>[0-9a-f]{24})/compatible/$", method=["GET"], access="read", api=True)
    def api_compatible(self, request, id):
        o = self.get_object_or_404(ObjectModel, id=id)
        # Connections
        r = []
        for c in o.connections:
            # Find compatible objects
            proposals = []
            for t, n in o.get_connection_proposals(c.name):
                m = ObjectModel.objects.filter(id=t).first()
                mc = m.get_model_connection(n)
                proposals += [
                    {
                        "model": m.name,
                        "model_description": m.description,
                        "name": n,
                        "description": mc.description,
                        "gender": mc.gender,
                    }
                ]
            #
            if (
                r
                and r[-1]["direction"] == c.direction
                and r[-1]["gender"] == c.gender
                and r[-1]["connections"] == proposals
            ):
                r[-1]["names"] += [{"name": c.name, "description": c.description}]
            else:
                r += [
                    {
                        "names": [{"name": c.name, "description": c.description}],
                        "direction": c.direction,
                        "gender": c.gender,
                        "connections": proposals,
                    }
                ]
        # Crossing
        # @todo: Count splitter interface
        rc = []
        for c in o.connections:
            if c.cross:
                rc += [{"y": c.name, "x": c.cross, "v": "1"}]
        return {"connections": r, "crossing": rc}

    @view(
        url="^actions/json/$",
        method=["POST"],
        access="read",
        validate={"ids": ListOfParameter(element=DocumentParameter(ObjectModel), convert=True)},
        api=True,
    )
    def api_action_json(self, request, ids):
        r = [o.json_data for o in ids]
        s = to_json(r, order=["name", "vendor__code", "description"])
        return {"data": s}
