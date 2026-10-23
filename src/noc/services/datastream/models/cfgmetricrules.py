# ----------------------------------------------------------------------
# cfgmetricrules datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.cdag.factory.config import GraphConfig


class RuleCondition(BaseModel):
    labels: list[str]
    exclude_labels: list[str] | None = None


class ActionInput(BaseModel):
    input_name: str
    probe_id: str
    sender_id: str


class RuleAction(BaseModel):
    id: str
    name: str
    graph_config: GraphConfig
    inputs: list[ActionInput]
    # outputs


class CfgMetricRule(BaseModel):
    id: str
    name: str
    actions: list[RuleAction]
    match: list[RuleCondition]
