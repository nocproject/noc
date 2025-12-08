# ----------------------------------------------------------------------
# vc.l2domainprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.vc.models.l2domainprofile import L2DomainProfile
from noc.core.translation import ugettext as _


class L2DomainProfileApplication(ExtDocApplication):
    """
    L2DomainProfile application
    """

    title = "L2Domain Profile"
    menu = [_("Setup"), _("L2Domain Profiles")]
    model = L2DomainProfile
