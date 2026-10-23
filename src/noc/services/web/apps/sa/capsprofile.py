# ----------------------------------------------------------------------
# sa.capsprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.capsprofile import CapsProfile
from noc.core.translation import ugettext as _


class CapsProfileApplication(ExtDocApplication):
    """
    CapsProfile application
    """

    title = "Caps Profile"
    menu = [_("Setup"), _("Caps Profiles")]
    model = CapsProfile
