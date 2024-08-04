# ----------------------------------------------------------------------
# IP Prefix Model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List

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
    state: Optional[str] = None
    # Last state change
    state_changed: Optional[datetime.datetime] = None
    # Workflow event
    event: Optional[str] = None
    description: Optional[str] = None
    parent: Optional[Reference["IPPrefix"]] = None
    vrf: Optional[Reference[IPVRF]] = None
    ipv6_transition: Optional[Reference["IPPrefix"]] = None
    project: Optional[Reference["Project"]] = None
    labels: Optional[List[str]] = None

    @field_validator("prefix")
    @classmethod
    def name_must_contain_space(cls, v: str) -> str:
        IPvAnyNetwork(v)
        return v.strip()
