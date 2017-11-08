# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# maintenance.maintenance application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.maintenance.models.maintenance import Maintenance


class MaintenanceApplication(ExtDocApplication):
    """
    Maintenance application
    """
    title = _("Maintenance")
    menu = _("Maintenance")
    model = Maintenance
    query_condition = "icontains"
    query_fields = ["subject"]

    @view(url="(?P<id>[0-9a-f]{24})/objects/", method=["GET"],
          access="read", api=True)
    def api_test(self, request, id):
        o = self.get_object_or_404(Maintenance, id=id)
        r = []
        for mao in o.affected_objects:
            mo = mao.object
            r += [
                {
                    "id": mo.id,
                    "name": mo.name,
                    "is_managed": mo.is_managed,
                    "profile": mo.profile.name,
                    # "platform": mo.platform,
                    # "administrative_domain": unicode(mo.administrative_domain),
                    "address": mo.address,
                    "description": mo.description,
                    "tags": mo.tags
                }
            ]
        return r
