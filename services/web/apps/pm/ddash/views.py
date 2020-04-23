# ---------------------------------------------------------------------
# pm.ddash application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from .dashboards.base import BaseDashboard
from .dashboards.mo import MODashboard
from .dashboards.mocard import MOCardDashboard
from .dashboards.link import LinkDashboard
from .dashboards.ipsla import IPSLADashboard
from .dashboards.container import ContainerDashboard
from noc.core.translation import ugettext as _


class DynamicDashboardApplication(ExtApplication):
    """
    MetricType application
    """

    title = _("Dynamic Dashboard")

    dashboards = {
        "mo": MODashboard,
        "mocard": MOCardDashboard,
        "link": LinkDashboard,
        "ipsla": IPSLADashboard,
        "container": ContainerDashboard,
    }

    @view(url=r"^$", method="GET", access="launch", api=True)
    def api_dashboard(self, request):
        dt = self.dashboards.get(request.GET.get("dashboard"))
        if not dt:
            return self.response_not_found("Dashboard not found")
        oid = request.GET.get("id")
        extra_vars = {}
        for v in request.GET:
            if v.startswith("var_"):
                extra_vars[v] = request.GET[v]
        extra_template = request.GET.get("extra_template")
        try:
            dashboard = dt(oid, extra_template, extra_vars)
        except BaseDashboard.NotFound:
            return self.response_not_found("Object not found")
        return dashboard.render()
