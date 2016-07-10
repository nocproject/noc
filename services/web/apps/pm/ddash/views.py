# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.ddash application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from dashboards.base import BaseDashboard
from dashboards.managedobject import ManagedObjectDashboard


class DynamicDashboardApplication(ExtApplication):
    """
    MetricType application
    """
    title = "Dynamic Dashboard"

    dashboards = {
        "managedobject": ManagedObjectDashboard
    }

    @view(
        url="^$", method="GET", access="launch", api=True
    )
    def api_dashboard(self, request):
        dt = self.dashboards.get(request.GET.get("dashboard"))
        if not dt:
            return self.response_not_found("Dashboard not found")
        oid = request.GET.get("id")
        try:
            dashboard = dt(oid)
        except BaseDashboard.NotFound:
            return self.response_not_found("Object not found")
        return dashboard.render()
