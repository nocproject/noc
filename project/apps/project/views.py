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
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
from noc.main.models.resourcestate import ResourceState


class ProjectApplication(ExtModelApplication):
    """
    Project application
    """
    title = "Project"
    menu = "Projects"
    model = Project
    query_condition = "icontains"
    query_fields = ["code", "name", "description"]

    @view(url="^(?P<id>\d+)/resources/$", access="read", method=["GET"],
          api=True)
    def api_resources(self, request, id):
        def f(o):
            if hasattr(o, "state") and o.state:
                state = o.state
            else:
                state = default_state
            return {
                "id": str(o.id),
                "label": unicode(o),
                "state_id": state.id,
                "state__label": state.name
            }
        project = self.get_object_or_404(Project, id=id)
        default_state = ResourceState.get_default()
        r = {
            "vc": [f(o) for o in project.vc_set.all()],
            "dnszone": [f(o) for o in project.dnszone_set.all()],
            "vrf": [f(o) for o in project.vrf_set.all()],
            "prefix": [f(o) for o in project.prefix_set.all()],
            "address": [f(o) for o in project.address_set.all()],
            "as": [f(o) for o in project.as_set.all()],
            "asset": [f(o) for o in project.asset_set.all()],
            "peer": [f(o) for o in project.peer_set.all()],
            "interface": [f(o) for o in Interface.objects.filter(project=project)],
            "subinterface": [f(o) for o in SubInterface.objects.filter(project=project)]
        }
        return r
