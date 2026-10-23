# ----------------------------------------------------------------------
# cfgalarm datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Literal, Any

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.models.valuetype import ValueType
from .utils import DisposeAction


class VarItem(BaseModel):
    name: str
    required: bool = False
    default_labels: list[str] | None = None
    default: str | None = None
    component: str | None = None
    # resource_model: Optional[str] = None


class VarTransformItem(BaseModel):
    name: str
    wildcard: str | None = None  # set from label
    required: bool = False
    affected_model: str | None = None
    alias: str | None = None
    value_type: ValueType | None = None
    update_oper_status: str | None = None


class ComboCondition(BaseModel):
    combo_condition: str
    combo_event_classes: list[str]
    combo_window: int = 0
    combo_count: int = 0


class RuleGroup(BaseModel):
    reference_template: str
    alarm_class: str | None = None
    title_template: str | None = None
    min_threshold: int = 0
    max_threshold: int = 1
    window: int = 0
    labels: list[str] | None = None


class RuleAction(BaseModel):
    """"""

    when: str
    action: str
    key: str
    template: str | None = None
    subject: str | None = None


class Rule(BaseModel):
    id: str
    name: str
    is_active: bool = True
    groups: list[RuleGroup] | None = None
    match_expr: list[dict[str, Any]] | None = None
    actions: list[RuleAction] | None = None
    rule_action: Literal["drop", "rewrite", "continue"] = "continue"
    rewrite_alarm_class: str | None = None
    severity_policy: str | None = None
    min_severity: int | None = None
    max_severity: int | None = None
    ttl_policy: str | None = None
    clear_after_ttl: int | None = None
    stop_processing: bool = False


class DispositionRule(BaseModel):
    name: str
    is_active: bool
    preference: int
    event_classes: list[str] | None = None
    stop_processing: bool = False
    action: Literal["ignore", "raise", "clear", "drop", "drop_mx"] = "ignore"
    match_expr: dict[str, Any] | None = None
    vars_match_expr: dict[str, Any] | None = None
    vars_transform: list[VarTransformItem] | None = None
    combo_condition: ComboCondition | None = None
    object_avail_condition: bool | None = None
    reference_lookup: bool = False
    # Target Actions
    actions: list[DisposeAction] | None = None
    # handlers


class CfgAlarm(BaseModel):
    id: str
    name: str
    bi_id: str
    is_unique: bool = False
    is_ephemeral: bool = False
    by_reference: bool = False
    reference: list[str] | None = None
    user_clearable: bool = False
    dispositions: list[DispositionRule] | None = None
    rules: list[Rule] | None = None
    # vars
    vars: list[VarItem] | None = None
    # subject:
    open_handlers: list[str] | None = None
    clear_handlers: list[str] | None = None
