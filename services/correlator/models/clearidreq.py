# ---------------------------------------------------------------------
# ClearId Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Literal

# Third-party modules
from pydantic import BaseModel, Field


class ClearIdRequest(BaseModel):
    op: Literal["clearid"] = Field(None, alias="$op")
    id: str
    timestamp: Optional[str] = None
    message: Optional[str] = None
    source: Optional[str] = None
