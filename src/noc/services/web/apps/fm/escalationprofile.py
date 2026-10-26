# ---------------------------------------------------------------------
# fm.escalationprofile application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.fm.models.escalationprofile import EscalationProfile
from noc.services.web.base.extdocapplication import ExtDocApplication


class EscalationProfileApplication(ExtDocApplication):
    """
    EscalationProfile application
    """

    title = _("Escalation Profile")
    menu = [_("Setup"), _("Escalation Profile")]
    model = EscalationProfile
