# ---------------------------------------------------------------------
# Clear Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Literal

# Third-party modules
from pydantic import BaseModel, Field


class ClearRequest(BaseModel):
    op: Literal["clear"] = Field(None, alias="$op")
    reference: str
    timestamp: str | None = None
    message: str | None = None
