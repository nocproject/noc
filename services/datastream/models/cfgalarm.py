# ----------------------------------------------------------------------
# cfgalarm datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from noc.core.models.cfgactions import ActionType
from typing import Optional, List, Literal, Dict, Any

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.models.valuetype import ValueType


class VarItem(BaseModel):
    name: str
    type: ValueType
    required: bool = False
    # resource_model: Optional[str] = None


class ComboCondition(BaseModel):
    combo_condition: str
    combo_event_classes: List[str]
    combo_window: int = 0
    combo_count: int = 0


class Rule(BaseModel):
    id: str
    name: str
    is_active: bool = True


class DisposeAction(BaseModel):
    """
    # Action
    # Run command
    # Run diagnostic
    # Run discovery (all/config)
    # Send workflow event
    # Set Diagnostic -> UP/DOWN
    # Audit
    """
    action: ActionType
    key: str
    # checks
    args: Optional[Dict[str, Any]] = None


class DisposeTargetObject(BaseModel):
    model: str = "sa.ManagedObject"
    actions: Optional[List[DisposeAction]]
    is_agent: bool = False
    # CPE, Agent
    # audit


class Resource(BaseModel):
    model: str
    actions: Optional[List[DisposeAction]]


class DispositionRule(BaseModel):
    name: str
    is_active: bool
    preference: int
    target: Optional[DisposeTargetObject] = None
    resources: Optional[List[Resource]] = None
    event_classes: Optional[List[str]] = None
    stop_processing: bool = False
    action: Literal["ignore", "raise", "clear", "drop", "drop_mx"] = "ignore"
    match_expr: Optional[Dict[str, Any]] = None
    vars_match_expr: Optional[Dict[str, Any]] = None
    var_mapping: Optional[Dict[str, str]] = None
    combo_condition: Optional[ComboCondition] = None
    object_avail_condition: Optional[str] = None
    # handlers


class CfgAlarm(BaseModel):
    id: str
    name: str
    bi_id: str
    is_unique: bool = False
    is_ephemeral: bool = False
    by_reference: bool = False
    reference: bool = False
    user_clearable: bool = False
    dispositions: Optional[List[DispositionRule]] = None
    rules: Optional[List[Rule]] = None
    # vars
    vars: Optional[List[VarItem]] = None
    # subject:
    open_handlers: List[str] = None
