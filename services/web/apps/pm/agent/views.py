# ----------------------------------------------------------------------
# pm.agent application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.services.web.base.decorators.state import state_handler
from noc.pm.models.agent import Agent
from noc.core.translation import ugettext as _
from noc.core.prettyjson import to_json


@state_handler
class AgentApplication(ExtDocApplication):
    """
    Agent application
    """

    title = "Agent"
    menu = [_("Setup"), _("Agent")]
    model = Agent

    @view(url="^(?P<id>[0-9a-f]{24})/config/$", method=["GET"], access="config", api=True)
    def api_config(self, request, id):
        from noc.services.zeroconf.util import get_config

        agent = self.get_object_or_404(Agent, id=id)
        cfg = get_config(agent).model_dump(by_alias=True)
        return to_json(cfg, order=["$type", "$version", "config", "collectors"])
