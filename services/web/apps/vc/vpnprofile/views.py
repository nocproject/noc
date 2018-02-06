# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# vc.vpnprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.vc.models.vpnprofile import VPNProfile
from noc.core.translation import ugettext as _


class VPNProfileApplication(ExtDocApplication):
    """
    VPNProfile application
    """
    title = "VPN Profiles"
    menu = [_("Setup"), _("VPN Profiles")]
    model = VPNProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
