# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## project.project application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.project.models import Project


class ProjectApplication(ExtModelApplication):
    """
    Project application
    """
    title = "Project"
    menu = "Projects"
    model = Project
    query_fields = ["code", "name"]

    @view(url="^(?P<id>\d+)/resources/$", access="read", method=["GET"],
          api=True)
    def api_resources(self, request, id):
        def f(o):
            return {
                "id": o.id,
                "label": unicode(o),
                "state_id": o.state.id if hasattr(o, "state") else None,
                "state__label": o.state.name if hasattr(o, "state") else None
            }
        project = self.get_object_or_404(Project, id=id)
        r = {
            "vc": [f(o) for o in project.vc_set.all()],
            "dnszone": [f(o) for o in project.dnszone_set.all()],
            "vrf": [f(o) for o in project.vrf_set.all()],
            "prefix": [f(o) for o in project.prefix_set.all()],
            "address": [f(o) for o in project.address_set.all()],
            "as": [f(o) for o in project.as_set.all()],
            "asset": [f(o) for o in project.asset_set.all()],
            "peer": [f(o) for o in project.peer_set.all()],
        }
        return r
