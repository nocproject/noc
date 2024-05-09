# ---------------------------------------------------------------------
# Event Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Literal

# Third-party modules
from pydantic import BaseModel, Field

# NOC modules
from noc.core.fm.event import Event


class EventRequest(BaseModel):
    op: Literal["event"] = Field(None, alias="$op")
    event_id: str
    event: Event  # In json form
