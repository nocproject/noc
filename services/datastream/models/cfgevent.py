# ----------------------------------------------------------------------
# cfgevent datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Literal, Dict

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.models.valuetype import ValueType


class VarItem(BaseModel):
    name: str
    type: ValueType
    required: bool = False
    match_suppress: bool = False


class ResourceMap(BaseModel):
    resource: Literal["if", "si", "ip"]
    include_path: bool = False
    admin_status: Optional[bool] = None
    oper_status: Optional[bool] = None


class ObjectResolver(BaseModel):
    scope: Literal["O", "S", "M"] = "M"
    # CPE (DyingGasp), RemoteSystem
    include_path: bool = True
    oper_status: Optional[bool] = None
    # workflow_event
    # diagnostic_status


class Action(BaseModel):
    # From rule
    rule_name: str
    handlers: List[str] = None
    notification_group: Optional[str] = None
    run_discovery: bool = False
    audit: Optional[int] = None
    # Conditions
    condition: Optional[str] = None


class FilterConfig(BaseModel):
    name: str
    window: int


class EventClass(BaseModel):
    id: str
    name: str
    bi_id: str


class CfgEvent(BaseModel):
    id: str
    name: str
    bi_id: str
    is_unique: bool = False
    event_class: EventClass
    managed_object_required: Optional[bool] = True
    filters: Dict[str, FilterConfig] = None
    # vars
    vars: Optional[List[VarItem]] = None
    # Object
    object_map: Optional[ObjectResolver] = None
    # Resource
    resources: Optional[List[ResourceMap]] = None
    # subject:
    handlers: List[str] = None
    actions: Optional[List[Action]] = None
    #
