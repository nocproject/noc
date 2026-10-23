# ----------------------------------------------------------------------
# pm.agentprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.pm.models.agentprofile import AgentProfile
from noc.core.translation import ugettext as _


class AgentProfileApplication(ExtDocApplication):
    """
    AgentProfile application
    """

    title = "Agent Profile"
    menu = [_("Setup"), _("Agent Profiles")]
    model = AgentProfile
