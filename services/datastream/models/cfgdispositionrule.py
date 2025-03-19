# ----------------------------------------------------------------------
# cfgdispositionrules datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Any, Dict, Tuple, Callable

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.fm.enum import EventSource


class Condition(BaseModel):
    event_class: str
    labels: Optional[List[str]] = None
    groups: Optional[List[str]] = None


class ComboCondition(BaseModel):
    condition: str
    window: int = 0
    count: int = 0


class RootCaseCondition(BaseModel):
    alarm_class: str
    window: int
    topology_rca: bool = False


class DispositionRule(BaseModel):
    name: str
    match: List[Condition]
    action: str
    is_active: bool = True
    preference: int = 1000
    alarm_class: Optional[str] = None
    combo_condition: Optional[ComboCondition] = None
    notification_group: Optional[str] = None
    subject_template: Optional[str] = None
    handlers: Optional[List[str]] = None
    root_cause: Optional[List[RootCaseCondition]] = None
    stop_processing: bool = True
