# ---------------------------------------------------------------------
# sla.slaprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sla.models.slaprofile import SLAProfile
from noc.core.translation import ugettext as _


class SLAProfileApplication(ExtDocApplication):
    """
    SLAProfile application
    """

    title = "SLA Profile"
    menu = [_("Setup"), _("SLA Profiles")]
    model = SLAProfile
