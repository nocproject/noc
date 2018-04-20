# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.objectmodel application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.main.models.doccategory import DocCategory
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.modelinterface import ModelInterface
from noc.sa.interfaces.base import ListOfParameter, DocumentParameter
from noc.lib.prettyjson import to_json


class ObjectModelApplication(ExtDocApplication):
    """
    ObjectModel application
    """
    title = "Object Models"
    menu = "Setup | Object Models"
    model = ObjectModel
    parent_model = DocCategory
    parent_field = "parent"
    query_fields = [
        "name__icontains",
        "description__icontains",
        "data__asset__part_no",
        "data__asset__order_part_no",
        "uuid"
    ]

    def clean(self, data):
        if "data" in data:
            data["data"] = ModelInterface.clean_data(data["data"])
        if "plugins" in data and data["plugins"]:
            data["plugins"] = [x.strip() for x in data["plugins"].split(",") if x.strip()]
        else:
            data["plugins"] = None
        return super(ObjectModelApplication, self).clean(data)

    def cleaned_query(self, q):
        if "is_container" in q:
            q["data__container__container"] = True
            q["name__ne"] = "Root"
            del q["is_container"]
        return super(ObjectModelApplication, self).cleaned_query(q)

    @view(url="^(?P<id>[0-9a-f]{24})/compatible/$", method=["GET"],
          access="read", api=True)
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
                proposals += [{
                    "model": m.name,
                    "model_description": m.description,
                    "name": n,
                    "description": mc.description,
                    "gender": mc.gender
                }]
            #
            if (r and r[-1]["direction"] == c.direction and
                        r[-1]["gender"] == c.gender and
                        r[-1]["connections"] == proposals):
                r[-1]["names"] += [{
                    "name": c.name,
                    "description": c.description
                }]
            else:
                r += [{
                    "names": [{
                        "name": c.name,
                        "description": c.description
                    }],
                    "direction": c.direction,
                    "gender": c.gender,
                    "connections": proposals
                }]
        # Crossing
        # @todo: Count splitter interface
        rc = []
        for c in o.connections:
            if c.cross:
                rc += [{
                    "y": c.name,
                    "x": c.cross,
                    "v": "1"
                }]
        return {
            "connections": r,
            "crossing": rc
        }

    @view(url="^actions/json/$", method=["POST"],
          access="read",
          validate={
            "ids": ListOfParameter(element=DocumentParameter(ObjectModel), convert=True)
          },
          api=True)
    def api_action_json(self, request, ids):
        r = [o.json_data for o in ids]
        s = to_json(r, order=["name", "vendor__code", "description"])
        return {"data": s}
