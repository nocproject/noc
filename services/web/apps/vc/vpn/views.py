# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc.vpn application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.vc.models.vpn import VPN
from noc.core.translation import ugettext as _
from noc.lib.app.decorators.state import state_handler


@state_handler
class VPNApplication(ExtDocApplication):
    """
    VPN application
    """
    title = "VPN"
    menu = [_("VPN")]
    model = VPN

    def field_row_class(self, o):
        return o.profile.style.css_class_name if o.profile.style else ""
