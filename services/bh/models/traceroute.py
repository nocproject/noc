# ---------------------------------------------------------------------
# Traceroute models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from gufo.traceroute import HopInfo
from pydantic import BaseModel


class TracerouteRequest(BaseModel):
    address: str
    timeout: Optional[int]
    tos: Optional[int]


class TracerouteResponse(BaseModel):
    status: bool
    end_address: str
    items: List[HopInfo]
