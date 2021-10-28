# ---------------------------------------------------------------------
# Clear Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # py3.7 support


# Third-party modules
from pydantic import BaseModel, Field


class ClearRequest(BaseModel):
    op: Literal["clear"] = Field(None, alias="$op")
    reference: str
    timestamp: Optional[str]
