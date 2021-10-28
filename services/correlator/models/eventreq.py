# ---------------------------------------------------------------------
# Event Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # py3.7 support


# Third-party modules
from pydantic import BaseModel, Field


class EventRequest(BaseModel):
    op: Literal["event"] = Field(None, alias="$op")
    event_id: str
    hint: Dict[str, Any]
