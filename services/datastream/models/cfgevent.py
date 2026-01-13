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
from noc.core.fm.enum import EventAction
from .utils import DisposeAction


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
    action: EventAction = EventAction.LOG
    # Disposition
    alarm_class: Optional[str] = None
    on_disposition: bool = False
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
    actions: Optional[List[DisposeAction]] = None


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
    link_event: bool = False
    filters: Optional[List[FilterConfig]] = None
    # vars
    vars: Optional[List[VarItem]] = None
    # subject:
    handlers: List[str] = None
    rules: Optional[List[Rule]] = None
