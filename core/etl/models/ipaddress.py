# ----------------------------------------------------------------------
# IP Address Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List

# Third-party modules
from pydantic.networks import IPvAnyAddress

# NOC modules
from .base import BaseModel
from .typing import Reference
from .ipprefix import IPPrefix
from .ipaddressprofile import IPAddressProfile


class IPAddress(BaseModel):
    id: str
    name: str
    prefix: Reference[IPPrefix]
    address: IPvAnyAddress
    profile: Reference["IPAddressProfile"]
    # Workflow state
    state: Optional[str] = None
    # Last state change
    state_changed: Optional[datetime.datetime] = None
    # Workflow event
    event: Optional[str] = None
    labels: Optional[List[str]] = None
