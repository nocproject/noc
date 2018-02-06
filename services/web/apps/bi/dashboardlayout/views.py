# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# bi.dashboardlayout application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.bi.models.dashboardlayout import DashboardLayout
from noc.core.translation import ugettext as _


class DashboardLayoutApplication(ExtDocApplication):
    """
    DashboardLayout application
    """
    title = "Dashboard Layout"
    menu = [_("Setup"), _("Dashboard Layout")]
    model = DashboardLayout

    @view(url="^(?P<id>[0-9a-f]{24})/json/$", method=["GET"],
          access="read", api=True)
    def api_json(self, request, id):
        layout = self.get_object_or_404(DashboardLayout, id=id)
        return layout.to_json()
