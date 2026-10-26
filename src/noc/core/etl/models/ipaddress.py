# ----------------------------------------------------------------------
# IP Address Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from pydantic import field_validator
from pydantic.networks import IPvAnyAddress

from .base import BaseModel
from .ipaddressprofile import IPAddressProfile
from .ipprefix import IPPrefix
from .typing import Reference


class IPAddress(BaseModel):
    id: str
    name: str
    address: str
    profile: Reference["IPAddressProfile"]
    fqdn: str | None = None
    # Workflow state
    prefix: Reference[IPPrefix] | None = None
    ipv6_transition: Reference["IPAddress"] | None = None
    state: str | None = None
    # Last state change
    state_changed: datetime.datetime | None = None
    # Workflow event
    event: str | None = None
    labels: list[str] | None = None

    @field_validator("address")
    @classmethod
    def name_must_contain_space(cls, v: str) -> str:
        IPvAnyAddress(v)
        return v.strip()
