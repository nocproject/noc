# ----------------------------------------------------------------------
# IP Prefix Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from pydantic import field_validator
from pydantic.networks import IPvAnyNetwork

from .base import BaseModel
from .ipprefixprofile import IPPrefixProfile
from .ipvrf import IPVRF
from .project import Project
from .typing import Reference


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
