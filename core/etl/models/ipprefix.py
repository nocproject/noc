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

# NOC modules
from .base import BaseModel
from .typing import Reference
from .ipvrf import IPVRF
from .project import Project
from .ipprefixprofile import IPPrefixProfile


class IPPrefix(BaseModel):
    id: str
    prefix: IPvAnyNetwork
    name: str
    profile: Reference["IPPrefixProfile"]
    # Workflow state
    state: Optional[str] = None
    # Last state change
    state_changed: Optional[datetime.datetime] = None
    # Workflow event
    event: Optional[str] = None
    parent: Optional[Reference["IPPrefix"]] = None
    vrf: Optional[Reference[IPVRF]]
    project: Optional[Reference["Project"]] = None
    labels: Optional[List[str]] = None
