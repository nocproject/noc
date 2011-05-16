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
from noc.inv.models import Model, ModelCategory, ObjectId, Socket


class ModelApplication(TreeApplication):
    title = "Models"
    verbose_name = "Model"
    verbose_name_plural = "Models"
    menu = "Setup | Models"
    model = Model
    category_model = ModelCategory
    list_display = [
        {
            "field": "name",
            "format": "short",
            "css": {
                "width": "150px"
            }
        },
        {
            "field": "description",
        }
    ]


    @view(url=r"^connections/popup/(?P<direction>[oic])/(?P<socket_type>[a-f0-9]+)/(?P<kind>[MF])/$",
          url_name="connections", access=HasPerm("view"))
    def view_connections_popup(self, request, direction, socket_type, kind):
        return self.render_tree_popup(request,
                            self.site.reverse("inv:model:lookup_connections",
                                              direction, socket_type, kind))
        
    @view(url=r"^connections/lookup/(?P<direction>[oic])/(?P<socket_type>[a-f0-9]+)/(?P<kind>[MF])/$",
          url_name="lookup_connections", access=HasPerm("view"))
    def view_conenctions_lookup(self, request, direction, socket_type, kind):
        def to_json(id, title, has_children):
            d = {"data": {"title": title}, "attr": {"id": "node_"+str(id)}}
            if has_children:
                d["state"] = "closed"
                d["attr"]["rel"] = "folder"
            else:
                d["data"]["attr"] = {"href": self.site.reverse("inv:model:preview", id), "target": "_"}
            return d

        k = {"M": "F", "F": "M"}[kind]
        f = "%s_sockets" % {"o": "i", "i": "o", "c": "c"}[direction]
        # Get possible types
        compatible_types = [ObjectId(socket_type)]
        s = Socket.objects.filter(id=compatible_types[0]).first()
        if s:
            if kind == "M" and s.m_compatible:
                compatible_types += [x.id for x in Socket.objects.filter(name__in=s.m_compatible)]
            elif kind == "F" and s.f_compatible:
                compatible_types += [x.id for x in Socket.objects.filter(name__in=s.f_compatible)]
        q = {
            f: {
                "$elemMatch": {
                    "kind": k,
                    "type": {
                        "$in": compatible_types
                    }
                }
            }
        }
        node = None
        if request.GET and "node" in request.GET:
            node = request.GET["node"]
            if node == "root":
                node = None
        if node is None:
            data = {
                "data": self.verbose_name_plural,
                "state": "closed",
                "attr": {"id": "node_root", "rel": "root"},
                "children": [to_json(*c) for c in self.get_children(None, filter=q)]
            }
        else:
            data = [to_json(*c) for c in self.get_children(node, filter=q)]
        return self.render_json(data)
