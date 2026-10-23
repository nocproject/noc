# ---------------------------------------------------------------------
# pm.ddash application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, api
from .dashboards.loader import loader
from .dashboards.base import BaseDashboard
from noc.core.translation import ugettext as _


class DynamicDashboardApplication(ExtApplication):
    """
    MetricType application
    """

    title = _("Dynamic Dashboard")

    @api.get(r"^$", access="launch")
    def api_dashboard(self, request: HttpRequest):
        dash_name = request.GET.get("dashboard")
        try:
            dt = loader[dash_name]
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
        print(dashboard, dashboard.template)
        return dashboard.render()
