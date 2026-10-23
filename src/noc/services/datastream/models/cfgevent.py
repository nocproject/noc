# ----------------------------------------------------------------------
# cfgevent datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Any

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
    resource_model: str | None = None


class ComboCondition(BaseModel):
    combo_condition: str
    combo_event_classes: list[str]
    combo_window: int = 0
    combo_count: int = 0


class Rule(BaseModel):
    name: str
    is_active: bool
    preference: int
    action: EventAction = EventAction.LOG
    # Disposition
    alarm_class: str | None = None
    on_disposition: bool = False
    stop_processing: bool = False
    # Conditions
    match_expr: dict[str, Any] | None = None
    vars_match_expr: dict[str, Any] | None = None
    combo_condition: ComboCondition | None = None
    # Actions
    handlers: list[str] | None = None
    # Notification
    notification_group: str | None = None
    subject_template: str | None = None
    # Target Actions
    actions: list[DisposeAction] | None = None


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
    to_dispose: bool = False
    link_event: bool = False
    filters: list[FilterConfig] | None = None
    # vars
    vars: list[VarItem] | None = None
    # subject:
    handlers: list[str] | None = None
    rules: list[Rule] | None = None
