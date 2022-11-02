# ----------------------------------------------------------------------
# main.messageroute application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication
from noc.main.models.messageroute import MessageRoute
from noc.core.translation import ugettext as _


class MessageRouteApplication(ExtDocApplication):
    """
    MessageRoute application
    """

    title = "Message Route"
    menu = [_("Setup"), _("Message Routes")]
    model = MessageRoute
    glyph = "arrows-alt"
