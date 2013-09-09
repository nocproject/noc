# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.managedobject application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models import ManagedObject, ManagedObjectAttribute
from noc.inv.models.link import Link
from noc.lib.app.modelinline import ModelInline
from noc.lib.app.repoinline import RepoInline


class ManagedObjectApplication(ExtModelApplication):
    """
    ManagedObject application
    """
    title = "Managed Objects"
    menu = "Managed Objects"
    model = ManagedObject
    query_condition = "icontains"
    # Inlines
    attrs = ModelInline(ManagedObjectAttribute)
    cfg = RepoInline("config")

    def field_platform(self, o):
        return o.platform

    def field_row_class(self, o):
        return o.object_profile.style.css_class_name if o.object_profile.style else ""

    @view(url="^(?P<id>\d+)/links/", method=["GET"],
          access="read", api=True)
    def api_links(self, request, id):
        o = self.get_object_or_404(ManagedObject, id=id)
        # Get links
        result = []
        for link in Link.object_links(o):
            l = []
            r = []
            for i in link.interfaces:
                if i.managed_object.id == o.id:
                    l += [i]
                else:
                    r += [i]
                for li, ri in zip(l, r):
                    result += [{
                        "id": str(link.id),
                        "local_interface": str(li.id),
                        "local_interface__label": li.name,
                        "remote_object": ri.managed_object.id,
                        "remote_object__label": ri.managed_object.name,
                        "remote_interface": str(ri.id),
                        "remote_interface__label": ri.name,
                        "discovery_method": link.discovery_method
                    }]
        return result
