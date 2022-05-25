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
from .object import Object
from .managedobject import ManagedObject


class Sensor(BaseModel):
    id: str
    local_id: str
    units: Optional[str]
    object: Optional[Reference["Object"]]
    managed_object: Reference["ManagedObject"]
    # Workflow state
    state: Optional[str]
    labels: List[str] = []
