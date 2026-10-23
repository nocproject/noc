# ----------------------------------------------------------------------
# vc.vpnprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.vc.models.vpnprofile import VPNProfile
from noc.core.translation import ugettext as _


class VPNProfileApplication(ExtDocApplication):
    """
    VPNProfile application
    """

    title = "VPN Profiles"
    menu = [_("Setup"), _("VPN Profiles")]
    model = VPNProfile
