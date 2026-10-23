# ----------------------------------------------------------------------
# vc.vlanprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.vc.models.vlanprofile import VLANProfile
from noc.core.translation import ugettext as _


class VLANProfileApplication(ExtDocApplication):
    """
    VLANProfile application
    """

    title = "VLAN Profile"
    menu = [_("Setup"), _("VLAN Profiles")]
    model = VLANProfile
