# ----------------------------------------------------------------------
# SensorModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# NOC modules
from .base import BaseModel, Reference


class Sensor(BaseModel):
    id: str
    local_id: str
    units: str
    object: Optional[Reference]
    managed_object: Optional[Reference]
    # Workflow state
    state: Optional[str]
    labels: List[str] = []
