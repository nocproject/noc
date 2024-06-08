# ----------------------------------------------------------------------
# IP VRF Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List

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
    state: Optional[str] = None
    # Last state change
    state_changed: Optional[datetime.datetime] = None
    # Workflow event
    event: Optional[str] = None
    rd: Optional[str] = "0:0"
    description: Optional[str] = None
    afi_ipv4: bool = True
    afi_ipv6: bool = False
    project: Optional[Reference["Project"]] = None
    labels: Optional[List[str]] = None
