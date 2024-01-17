# ----------------------------------------------------------------------
# PurgatoriumModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Any

# NOC modules
from .base import BaseModel, _BaseModel


class ObjectData(_BaseModel):
    attr: str
    value: Any


class DiscoveredObject(BaseModel):
    id: str
    address: str
    pool: str
    hostname: Optional[str] = None
    chassis_id: Optional[str] = None
    data: List[ObjectData] = []
    checkpoint: Optional[str] = None
    