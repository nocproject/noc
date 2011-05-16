# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.vendor application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011
## The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import TreeApplication, view, HasPerm, site
from noc.inv.models import Vendor, ObjectId


class VendorApplication(TreeApplication):
    title = "Vendors"
    verbose_name = "Vendor"
    verbose_name_plural = "Vendors"
    menu = "Setup | Vendors"
    model = Vendor

    @view(url=r"^(?P<vendor>[a-f0-9]+)/models/$",
          url_name="models", access=HasPerm("view"))
    def view_models_popup(self, request, vendor):
        return self.render_tree_popup(request,
                            self.site.reverse("inv:vendor:lookup_models",
                                              vendor),
                            css_url=self.site.reverse("inv:model:tree_css"))
    
    @view(url=r"^(?P<vendor>[a-f0-9]+)/models/lookup/$",
          url_name="lookup_models", access=HasPerm("view"))
    def view_models_lookup(self, request, vendor):
        def to_json(id, title, has_children):
            d = {"data": {"title": title}, "attr": {"id": "node_"+str(id)}}
            if has_children:
                d["state"] = "closed"
                d["attr"]["rel"] = "folder"
            else:
                d["data"]["attr"] = {"href": self.site.reverse("inv:model:preview", id), "target": "_"}
            return d
        
        q = {"vendor": ObjectId(vendor)}
        get_children = self.site.apps["inv.model"].get_children
        node = None
        if request.GET and "node" in request.GET:
            node = request.GET["node"]
            if node == "root":
                node = None
        if node is None:
            data = {
                "data": "Models",
                "state": "closed",
                "attr": {"id": "node_root", "rel": "root"},
                "children": [to_json(*c) for c in get_children(None, filter=q)]
            }
        else:
            data = [to_json(*c) for c in get_children(node, filter=q)]
        return self.render_json(data)

