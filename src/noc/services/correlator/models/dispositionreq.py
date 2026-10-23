# ---------------------------------------------------------------------
# Raise Request By Reference
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any, Literal

# Third-party modules
from pydantic import BaseModel, Field

# NOC modules
from noc.core.fm.enum import EventSeverity


class GroupItem(BaseModel):
    reference: str
    alarm_class: str | None = None
    name: str | None = None


class Event(BaseModel):
    id: str | None = None
    event_class: str | None = None
    severity: EventSeverity | None = None


class DispositionRequest(BaseModel):
    op: Literal["disposition"] = Field(None, alias="$op")
    reference: str
    alarm_class: str | None = None
    severity: int | None = None
    timestamp: str | None = None
    groups: list[GroupItem] | None = None
    vars: dict[str, Any] | None = None
    labels: list[str] | None = None
    managed_object: str | None = None
    remote_system: str | None = None
    remote_id: str | None = None
    name: str | None = None
    subject: str | None = None
    event: Event | None = None
    # For Event Block
    # services: Optional[List[str]] = None
