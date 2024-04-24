# ----------------------------------------------------------------------
# inv.channel application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
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
