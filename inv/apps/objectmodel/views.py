# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.objectmodel application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Pytohn modules
from collections import defaultdict
## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.connectiontype import ConnectionType
from noc.sa.interfaces.base import ListOfParameter, DocumentParameter
from noc.lib.prettyjson import to_json


class ObjectModelApplication(ExtDocApplication):
    """
    ObjectModel application
    """
    title = "Object Models"
    menu = "Setup | Object Models"
    model = ObjectModel
    query_fields = ["name__icontains", "description__icontains"]

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_to_json(self, request, id):
        o = self.get_object_or_404(ObjectModel, id=id)
        return o.to_json()

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
            r += [{
                "name": c.name,
                "description": c.description,
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
            "ids": ListOfParameter(element=DocumentParameter(ObjectModel))
          },
          api=True)
    def api_action_json(self, request, ids):
        r = [o.json_data for o in ids]
        s = to_json(r, order=["name", "vendor__code", "description"])
        return {"data": s}
