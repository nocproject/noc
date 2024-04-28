# ---------------------------------------------------------------------
# fm.escalationprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.fm.models.escalationprofile import EscalationProfile
from noc.core.translation import ugettext as _


class EscalationProfileApplication(ExtDocApplication):
    """
    EscalationProfile application
    """

    title = _("Escalation Profile")
    menu = [_("Setup"), _("Escalation Profile")]
    model = EscalationProfile
