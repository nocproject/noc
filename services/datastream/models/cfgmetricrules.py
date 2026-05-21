# ----------------------------------------------------------------------
# cfgmetricrules datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.cdag.factory.config import GraphConfig


class RuleCondition(BaseModel):
    labels: List[str]
    exclude_labels: Optional[List[str]] = None


class ActionInput(BaseModel):
    input_name: str
    probe_id: str
    sender_id: str


class RuleAction(BaseModel):
    id: str
    name: str
    graph_config: GraphConfig
    inputs: List[ActionInput]
    # outputs


class CfgMetricRule(BaseModel):
    id: str
    name: str
    actions: List[RuleAction]
    match: List[RuleCondition]
