# ---------------------------------------------------------------------
# EnsureGroup Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, List, Literal

# Third-party modules
from pydantic import BaseModel, Field

# NOC modules
from noc.core.fm.enum import GroupType


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
    g_type: GroupType = GroupType.GROUP
    severity: Optional[int] = None
    name: Optional[str] = None
    alarm_class: Optional[str] = None
    labels: Optional[List[str]] = None
    vars: Optional[Dict[str, Any]] = None
    alarms: List[AlarmItem]
