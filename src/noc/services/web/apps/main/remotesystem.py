# ----------------------------------------------------------------------
# main.remotesystem application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, api
from noc.main.models.remotesystem import RemoteSystem
from noc.core.translation import ugettext as _


class RemoteSystemApplication(ExtDocApplication):
    """
    RemoteSystem application
    """

    title = "Remote System"
    menu = [_("Setup"), _("Remote Systems")]
    model = RemoteSystem

    @api.get("^brief_lookup/$", access="lookup")
    def api_brief(self, request: HttpRequest):
        return [
            {
                "id": str(rs.id),
                "label": rs.name,
                "last_successful_load": (
                    rs.last_successful_load.strftime("%Y-%m-%d %H:%M")
                    if rs.last_successful_load
                    else _("never")
                ),
            }
            for rs in RemoteSystem.objects.filter()
        ]
