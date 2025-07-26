# ----------------------------------------------------------------------
# cfgevent datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Any

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.models.valuetype import ValueType


class TargetAction(BaseModel):
    interaction_audit: int
    run_discovery: bool = False
    update_avail: bool = False


class VarItem(BaseModel):
    name: str
    type: ValueType
    required: bool = False
    match_suppress: bool = False
    resource_model: Optional[str] = None


class ComboCondition(BaseModel):
    combo_condition: str
    combo_event_classes: List[str]
    combo_window: int = 0
    combo_count: int = 0


class Rule(BaseModel):
    name: str
    is_active: bool
    preference: int
    event_classes: List[str]
    action: str = "ignore"
    # Disposition
    alarm_class: Optional[str] = None
    ignore_target_on_dispose: bool = False
    stop_processing: bool = False
    # Conditions
    match_expr: Optional[Dict[str, Any]] = None
    vars_match_expr: Optional[Dict[str, Any]] = None
    combo_condition: Optional[ComboCondition] = None
    # Actions
    handlers: Optional[List[str]] = None
    # Notification
    notification_group: Optional[str] = None
    subject_template: Optional[str] = None
    # Target Actions
    object_actions: Optional[TargetAction] = None
    resource_oper_status: Optional[str] = None


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
    event_class: EventClass
    is_unique: bool = False
    filters: Dict[str, FilterConfig] = None
    # vars
    vars: Optional[List[VarItem]] = None
    # subject:
    handlers: List[str] = None
    actions: Optional[List[Rule]] = None
    #
