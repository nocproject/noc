# ---------------------------------------------------------------------
# phone.phonerangeprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.phone.models.phonerangeprofile import PhoneRangeProfile
from noc.core.translation import ugettext as _


class PhoneRangeProfileApplication(ExtDocApplication):
    """
    PhoneRangeProfile application
    """

    title = "Phone Range Profile"
    menu = [_("Setup"), _("Range Profile")]
    model = PhoneRangeProfile
