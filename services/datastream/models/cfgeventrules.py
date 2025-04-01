# ----------------------------------------------------------------------
# cfgeventrules datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.fm.enum import EventSource


class ClassificationPattern(BaseModel):
    key_re: str
    value_re: str


class RuleVar(BaseModel):
    name: str
    value: str


class ClassificationRule(BaseModel):
    id: str
    name: str
    event_class: str
    event_class_id: str
    source: Optional[List[EventSource]] = None
    profiles: Optional[List[str]] = None
    preference: int = 1000
    message_rx: Optional[str] = None
    patterns: Optional[List[ClassificationPattern]] = None
    vars: Optional[List[RuleVar]] = None
    labels: Optional[List[str]]
    to_dispose: bool = False
