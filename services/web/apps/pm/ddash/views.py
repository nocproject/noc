# ---------------------------------------------------------------------
# pm.ddash application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from .dashboards.loader import loader
from .dashboards.base import BaseDashboard
from noc.core.translation import ugettext as _


class DynamicDashboardApplication(ExtApplication):
    """
    MetricType application
    """

    title = _("Dynamic Dashboard")

    @view(url=r"^$", method="GET", access="launch", api=True)
    def api_dashboard(self, request):
        try:
            dt = loader[request.GET.get("dashboard")]
        except Exception:
            self.logger.error("Exception when loading dashboard: %s", request.GET.get("dashboard"))
            return self.response_not_found("Dashboard not found")
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
