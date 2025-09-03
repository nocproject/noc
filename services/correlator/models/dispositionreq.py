# ---------------------------------------------------------------------
# Raise Request By Reference
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, List, Literal

# Third-party modules
from pydantic import BaseModel, Field

# NOC modules
from noc.core.fm.enum import EventSeverity


class GroupItem(BaseModel):
    reference: str
    alarm_class: Optional[str] = None
    name: Optional[str] = None


class Event(BaseModel):
    id: Optional[str] = None
    event_class: Optional[str] = None
    severity: Optional[EventSeverity] = None


class DispositionRequest(BaseModel):
    op: Literal["disposition"] = Field(None, alias="$op")
    reference: str
    alarm_class: Optional[str] = None
    severity: Optional[int] = None
    timestamp: Optional[str] = None
    groups: Optional[List[GroupItem]] = None
    vars: Optional[Dict[str, Any]] = None
    labels: Optional[List[str]] = None
    managed_object: Optional[str] = None
    remote_system: Optional[str] = None
    remote_id: Optional[str] = None
    name: Optional[str] = None
    subject: Optional[str] = None
    event: Optional[Event] = None
    # For Event Block
    # services: Optional[List[str]] = None
