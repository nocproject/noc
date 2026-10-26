# ----------------------------------------------------------------------
# ip.addressprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.ip.models.addressprofile import AddressProfile
from noc.services.web.base.extdocapplication import ExtDocApplication


class AddressProfileApplication(ExtDocApplication):
    """
    AddressProfile application
    """

    title = "Address Profile"
    menu = [_("Setup"), _("Address Profiles")]
    model = AddressProfile
    implied_permissions = {"launch": ["main:template:lookup"]}
