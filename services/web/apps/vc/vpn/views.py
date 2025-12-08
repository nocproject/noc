# ----------------------------------------------------------------------
# vc.vpn application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.vc.models.vpn import VPN
from noc.core.translation import ugettext as _
from noc.services.web.base.decorators.state import state_handler


@state_handler
class VPNApplication(ExtDocApplication):
    """
    VPN application
    """

    title = "VPN"
    menu = [_("VPN")]
    model = VPN
