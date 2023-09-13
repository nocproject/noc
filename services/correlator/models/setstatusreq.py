# ---------------------------------------------------------------------
# SetStatus Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Literal, List

# Third-party modules
from pydantic import BaseModel, Field


class StatusItem(BaseModel):
    managed_object: str
    status: bool
    timestamp: Optional[str] = None
    labels: Optional[List[str]] = None


class SetStatusRequest(BaseModel):
    op: Literal["set_status"] = Field(None, alias="$op")
    statuses: List[StatusItem]
