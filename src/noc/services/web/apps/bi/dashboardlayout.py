# ---------------------------------------------------------------------
# bi.dashboardlayout application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, api
from noc.bi.models.dashboardlayout import DashboardLayout
from noc.core.translation import ugettext as _


class DashboardLayoutApplication(ExtDocApplication):
    """
    DashboardLayout application
    """

    title = "Dashboard Layout"
    menu = [_("Setup"), _("Dashboard Layout")]
    model = DashboardLayout

    @api.get("^(?P<id>[0-9a-f]{24})/json/$", access="read")
    def api_json(self, request: HttpRequest, id):
        layout = self.get_object_or_404(DashboardLayout, id=id)
        return layout.to_json()
