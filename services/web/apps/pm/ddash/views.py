# ---------------------------------------------------------------------
# pm.ddash application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.sa.models.managedobject import ManagedObject
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
        dash_name = request.GET.get("dashboard")
        try:
            # ddash by cals
            oid = request.GET.get("id")
            mo = ManagedObject.get_by_id(oid)
            if mo.get_caps().get("Sensor | Controller"):
                dash_name = "sensor_controller"
            if mo.get_caps().get("Network | DVBC"):
                dash_name = "modvbc"
        except Exception:
            pass
        try:
            dt = loader[dash_name]
        except Exception:
            self.logger.error("Exception when loading dashboard: %s", request.GET.get("dashboard"))
            return self.response_not_found("Dashboard not found")
        if not dt:
            return self.response_not_found("Dashboard not found")
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
