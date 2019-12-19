# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.resourcegroup application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.inv.models.resourcegroup import ResourceGroup
from noc.core.comp import smart_text
from noc.core.translation import ugettext as _


class ResourceGroupApplication(ExtDocApplication):
    """
    ResourceGroup application
    """

    title = "ResourceGroup"
    menu = [_("Setup"), _("Resource Groups")]
    model = ResourceGroup
    query_fields = ["name"]
    query_condition = "icontains"

    def instance_to_lookup(self, o, fields=None):
        return {"id": str(o.id), "label": smart_text(o), "has_children": o.has_children}

    @view("^(?P<id>[0-9a-f]{24})/get_path/$", access="read", api=True)
    def api_get_path(self, request, id):
        o = self.get_object_or_404(ResourceGroup, id=id)
        path = [ResourceGroup.get_by_id(rg) for rg in o.get_path()]
        return {
            "data": [
                {"level": level + 1, "id": str(p.id), "label": smart_text(p.name)}
                for level, p in enumerate(path)
            ]
        }
