# ----------------------------------------------------------------------
# cfgalarm datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Literal, Dict, Any

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.models.valuetype import ValueType
from .utils import DisposeAction


class VarItem(BaseModel):
    name: str
    required: bool = False
    default_labels: Optional[List[str]] = None
    default: Optional[str] = None
    component: Optional[str] = None
    # resource_model: Optional[str] = None


class VarTransformItem(BaseModel):
    name: str
    wildcard: Optional[str] = None  # set from label
    required: bool = False
    affected_model: Optional[str] = None
    alias: Optional[str] = None
    value_type: Optional[ValueType] = None
    update_oper_status: Optional[str] = None


class ComboCondition(BaseModel):
    combo_condition: str
    combo_event_classes: List[str]
    combo_window: int = 0
    combo_count: int = 0


class RuleGroup(BaseModel):
    reference_template: str
    alarm_class: Optional[str] = None
    title_template: Optional[str] = None
    min_threshold: int = 0
    max_threshold: int = 1
    window: int = 0
    labels: Optional[List[str]] = None


class RuleAction(BaseModel):
    """"""

    when: str
    action: str
    key: str
    template: Optional[str] = None
    subject: Optional[str] = None


class Rule(BaseModel):
    id: str
    name: str
    is_active: bool = True
    groups: Optional[List[RuleGroup]] = None
    match_expr: Optional[List[Dict[str, Any]]] = None
    actions: Optional[List[RuleAction]] = None
    rule_action: Literal["drop", "rewrite", "continue"] = "continue"
    rewrite_alarm_class: Optional[str] = None
    severity_policy: Optional[str] = None
    min_severity: Optional[int] = None
    max_severity: Optional[int] = None
    ttl_policy: Optional[str] = None
    clear_after_ttl: Optional[int] = None
    stop_processing: bool = False


class DispositionRule(BaseModel):
    name: str
    is_active: bool
    preference: int
    event_classes: Optional[List[str]] = None
    stop_processing: bool = False
    action: Literal["ignore", "raise", "clear", "drop", "drop_mx"] = "ignore"
    match_expr: Optional[Dict[str, Any]] = None
    vars_match_expr: Optional[Dict[str, Any]] = None
    vars_transform: Optional[List[VarTransformItem]] = None
    combo_condition: Optional[ComboCondition] = None
    object_avail_condition: Optional[bool] = None
    reference_lookup: bool = False
    # Target Actions
    actions: Optional[List[DisposeAction]] = None
    # handlers


class CfgAlarm(BaseModel):
    id: str
    name: str
    bi_id: str
    is_unique: bool = False
    is_ephemeral: bool = False
    by_reference: bool = False
    reference: Optional[List[str]] = None
    user_clearable: bool = False
    dispositions: Optional[List[DispositionRule]] = None
    rules: Optional[List[Rule]] = None
    # vars
    vars: Optional[List[VarItem]] = None
    # subject:
    open_handlers: Optional[List[str]] = None
    clear_handlers: Optional[List[str]] = None
