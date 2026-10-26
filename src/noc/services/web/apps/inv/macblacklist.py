# ----------------------------------------------------------------------
# inv.macblacklist application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.inv.models.macblacklist import MACBlacklist
from noc.services.web.base.extdocapplication import ExtDocApplication


class MACBlacklistApplication(ExtDocApplication):
    """
    MACBlacklist application
    """

    title = "MAC Blacklist"
    menu = [_("Setup"), _("MAC Blacklist")]
    model = MACBlacklist
