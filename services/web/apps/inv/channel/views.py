# ----------------------------------------------------------------------
# inv.channel application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.inv.models.channel import Channel
from noc.inv.models.endpoint import Endpoint
from noc.core.translation import ugettext as _
from noc.services.web.base.docinline import DocInline


class ChannelApplication(ExtDocApplication):
    """
    Channel application
    """

    title = _("Channels")
    menu = [_("Channels")]
    model = Channel
    glyph = "road"
    endpoints = DocInline(Endpoint)
    parent_model = Channel
    parent_field = "parent"

    @view(url="^(?P<id>[0-9a-f]{24})/dot/", method=["GET"], api=True, access="read")
    def api_dot(self, request, id: str):
        r = ["graph {"]
        r.append("  A -- B")
        r.append("}")
        return self.render_json({"dot": "\n".join(r)})
