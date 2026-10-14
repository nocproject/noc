# ----------------------------------------------------------------------
# pm.agent application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.services.web.base.decorators.state import state_handler
from noc.pm.models.agent import Agent
from noc.core.translation import ugettext as _


@state_handler
class AgentApplication(ExtDocApplication):
    """
    Agent application
    """

    title = "Agent"
    menu = [_("Setup"), _("Agent")]
    model = Agent
