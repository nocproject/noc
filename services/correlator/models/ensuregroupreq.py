# ---------------------------------------------------------------------
# EnsureGroup Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, List, Literal

# Third-party modules
from pydantic import BaseModel, Field


class AlarmItem(BaseModel):
    reference: str
    managed_object: str
    alarm_class: str
    severity: Optional[int] = None
    timestamp: Optional[str] = None
    vars: Optional[Dict[str, Any]] = None
    labels: Optional[List[str]] = None
    remote_system: Optional[str] = None
    remote_id: Optional[str] = None


class EnsureGroupRequest(BaseModel):
    op: Literal["ensure_group"] = Field(None, alias="$op")
    reference: str
    name: Optional[str] = None
    alarm_class: Optional[str] = None
    labels: Optional[List[str]] = None
    alarms: List[AlarmItem]
