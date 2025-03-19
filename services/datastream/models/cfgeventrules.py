# ----------------------------------------------------------------------
# cfgeventrules datastream model
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


class ClassificationPattern(BaseModel):
    key_re: str
    value_re: str


class RuleVar(BaseModel):
    name: str
    value: str


class ClassificationRule(BaseModel):
    name: str
    event_class: str
    source: Optional[List[EventSource]] = None
    profiles: Optional[List[str]] = None
    preference: int = 100
    message_rx: Optional[str] = None
    patterns: Optional[List[ClassificationPattern]] = None
    vars: Optional[List[RuleVar]] = None
    to_dispose: bool = False
