# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.model application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011
## The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import TreeApplication, view, HasPerm
from noc.inv.models import Model, ModelCategory, ObjectId


class ModelApplication(TreeApplication):
    title = "Models"
    verbose_name = "Model"
    verbose_name_plural = "Models"
    menu = "Setup | Models"
    model = Model
    category_model = ModelCategory

    @view(url=r"^connections/(?P<direction>[oic])/(?P<socket_type>[a-f0-9]+)/(?P<kind>[MF])/$",
          url_name="connections", access=HasPerm("view"))
    def view_connections(self, request, direction, socket_type, kind):
        k = {"M": "F", "F": "M"}[kind]
        f = "%s_sockets" % {"o": "i", "i": "o", "c": "c"}[direction]
        # > db.noc.models.find({"i_sockets": {$elemMatch: {"kind": "F", "type": ObjectId("4dcc4d7a5a2090675d000002")}} }, {"name": 1})
        q = {
            f: {
                "$elemMatch": {
                    "kind": k,
                    "type": ObjectId(socket_type)
                }
            }
        }
        connections = Model.objects.filter(__raw__=q).order_by("name")
        return self.render(request, "connections.html", connections=connections)
