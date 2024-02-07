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
from pydantic import field_validator

# NOC modules
from .base import BaseModel
from .typing import Reference
from .ipprefix import IPPrefix
from .ipaddressprofile import IPAddressProfile


class IPAddress(BaseModel):
    id: str
    name: str
    address: str
    profile: Reference["IPAddressProfile"]
    fqdn: Optional[str] = None
    # Workflow state
    prefix: Optional[Reference[IPPrefix]] = None
    ipv6_transition: Optional[Reference["IPAddress"]] = None
    state: Optional[str] = None
    # Last state change
    state_changed: Optional[datetime.datetime] = None
    # Workflow event
    event: Optional[str] = None
    labels: Optional[List[str]] = None

    @field_validator("address")
    @classmethod
    def name_must_contain_space(cls, v: str) -> str:
        IPvAnyAddress(v)
        return v.strip()
