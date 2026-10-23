# ----------------------------------------------------------------------
# IP VRF Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from .base import BaseModel
from .typing import Reference
from .project import Project


class IPVRF(BaseModel):
    id: str
    name: str
    profile: str
    vpn_id: str
    # Workflow state
    state: str | None = None
    # Last state change
    state_changed: datetime.datetime | None = None
    # Workflow event
    event: str | None = None
    rd: str | None = "0:0"
    description: str | None = None
    afi_ipv4: bool = True
    afi_ipv6: bool = False
    project: Reference["Project"] | None = None
    labels: list[str] | None = None
