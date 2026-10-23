# ---------------------------------------------------------------------
# Raise Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Any, Literal

# Third-party modules
from pydantic import BaseModel, Field


class GroupItem(BaseModel):
    reference: str
    alarm_class: str | None = None
    name: str | None = None


class RaiseRequest(BaseModel):
    op: Literal["raise"] = Field(None, alias="$op")
    reference: str
    managed_object: str
    alarm_class: str
    severity: int | None = None
    timestamp: str | None = None
    groups: list[GroupItem] | None = None
    vars: dict[str, Any] | None = None
    labels: list[str] | None = None
    remote_system: str | None = None
    remote_id: str | None = None
