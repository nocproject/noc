# ----------------------------------------------------------------------
# PMAgent loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any

# NOC modules
from .base import BaseLoader
from ..models.pmagent import PMAgent
from noc.pm.models.agent import Agent as AgentModel
from noc.pm.models.agentprofile import AgentProfile
from noc.inv.models.capability import Capability


class PMAgentLoader(BaseLoader):
    """
    Sensor loader
    """

    name = "pmagent"
    model = AgentModel
    data_model = PMAgent

    discard_deferred = True
    workflow_event_model = True
    remote_mappings_supported = True
    label_enable_setting = "enable_agent"

    ignore_unique = {"bi_id", "key"}

    model_mappings = {"profile": AgentProfile}

    post_save_fields = {"capabilities", "addresses"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_caps = {x.name for x in Capability.objects.filter()}

    def post_save(self, o: AgentModel, fields: Dict[str, Any]):
        if not fields:
            capabilities, addresses = [], []
        else:
            capabilities, addresses = fields.get("capabilities"), fields.get("addresses")
        caps = {}
        for cc in capabilities or []:
            c_name = cc["name"]
            if c_name not in self.available_caps:
                continue
            caps[c_name] = cc["value"]
        o.update_caps(caps, source="etl", scope=self.system.name)
        o.update_addresses(ip=addresses)
