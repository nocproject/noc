# ----------------------------------------------------------------------
# main.remotesystem application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.main.models.remotesystem import RemoteSystem
from noc.core.translation import ugettext as _


class RemoteSystemApplication(ExtDocApplication):
    """
    RemoteSystem application
    """

    title = "Remote System"
    menu = [_("Setup"), _("Remote Systems")]
    model = RemoteSystem

    @view(method=["GET"], url="^brief_lookup/$", access="lookup", api=True)
    def api_brief(self, request):
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
