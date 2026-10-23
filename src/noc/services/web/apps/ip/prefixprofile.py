# ----------------------------------------------------------------------
# ip.prefixprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.ip.models.prefixprofile import PrefixProfile
from noc.core.translation import ugettext as _


class PrefixProfileApplication(ExtDocApplication):
    """
    PrefixProfile application
    """

    title = _("Prefix Profile")
    menu = [_("Setup"), _("Prefix Profiles")]
    model = PrefixProfile
