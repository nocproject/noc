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
        return r
