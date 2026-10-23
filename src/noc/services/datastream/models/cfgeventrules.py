# ----------------------------------------------------------------------
# cfgeventrules datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Literal

# Third-party modules
from pydantic import BaseModel, Field

# NOC modules
from noc.core.fm.enum import EventSource


class ClassificationPattern(BaseModel):
    key_re: str
    value_re: str


class RuleVar(BaseModel):
    name: str
    value: str


class EventClass(BaseModel):
    id: str
    name: str


class ClassificationRule(BaseModel):
    id: str
    name: str
    rule: Literal["classification", "ignore_pattern"] = Field(None, alias="$type")
    event_class: EventClass | None = None
    source: list[EventSource] | None = None
    profiles: list[str] | None = None
    preference: int = 1000
    message_rx: str | None = None
    patterns: list[ClassificationPattern] | None = None
    vars: list[RuleVar] | None = None
    labels: list[str] | None
    to_dispose: bool = False
