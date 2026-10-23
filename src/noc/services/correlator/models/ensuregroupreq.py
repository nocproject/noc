# ---------------------------------------------------------------------
# EnsureGroup Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any, Literal

# Third-party modules
from pydantic import BaseModel, Field

# NOC modules
from noc.core.fm.enum import GroupType


class AlarmItem(BaseModel):
    reference: str
    managed_object: str
    alarm_class: str
    severity: int | None = None
    timestamp: str | None = None
    vars: dict[str, Any] | None = None
    labels: list[str] | None = None
    remote_system: str | None = None
    remote_id: str | None = None


class EnsureGroupRequest(BaseModel):
    op: Literal["ensure_group"] = Field(None, alias="$op")
    reference: str
    g_type: GroupType = GroupType.GROUP
    severity: int | None = None
    name: str | None = None
    alarm_class: str | None = None
    labels: list[str] | None = None
    vars: dict[str, Any] | None = None
    alarms: list[AlarmItem]
