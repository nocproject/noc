# ----------------------------------------------------------------------
# IP Prefix Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from pydantic.networks import IPvAnyNetwork
from pydantic import field_validator

# NOC modules
from .base import BaseModel
from .typing import Reference
from .ipvrf import IPVRF
from .project import Project
from .ipprefixprofile import IPPrefixProfile


class IPPrefix(BaseModel):
    id: str
    prefix: str
    name: str
    profile: Reference["IPPrefixProfile"]
    # Workflow state
    state: str | None = None
    # Last state change
    state_changed: datetime.datetime | None = None
    # Workflow event
    event: str | None = None
    description: str | None = None
    parent: Reference["IPPrefix"] | None = None
    vrf: Reference[IPVRF] | None = None
    ipv6_transition: Reference["IPPrefix"] | None = None
    project: Reference["Project"] | None = None
    labels: list[str] | None = None

    @field_validator("prefix")
    @classmethod
    def name_must_contain_space(cls, v: str) -> str:
        IPvAnyNetwork(v)
        return v.strip()
