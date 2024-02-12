# ----------------------------------------------------------------------
# PurgatoriumModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, List
from noc.core.purgatorium import ProtocolCheckResult

# NOC modules
from .base import BaseModel


class DiscoveredObject(BaseModel):
    id: str
    address: str
    pool: str
    hostname: Optional[str] = None
    chassis_id: Optional[str] = None
    description: Optional[str] = None
    labels: Optional[List[str]] = None
    checks: Optional[List[ProtocolCheckResult]] = None
    data: Dict[str, str] = None
