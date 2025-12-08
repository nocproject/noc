# ----------------------------------------------------------------------
# peer.asprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.peer.models.asprofile import ASProfile
from noc.core.translation import ugettext as _


class ASProfileApplication(ExtDocApplication):
    """
    ASProfile application
    """

    title = "AS Profile"
    menu = [_("Setup"), _("AS Profiles")]
    model = ASProfile
