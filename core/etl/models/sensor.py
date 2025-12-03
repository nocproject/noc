# ----------------------------------------------------------------------
# SensorModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# NOC modules
from noc.core.models.sensorprotos import SensorProtocol
from .base import BaseModel, Reference
from .object import Object
from .managedobject import ManagedObject
from .pmagent import PMAgent


class Sensor(BaseModel):
    id: str
    local_id: str
    label: Optional[str] = None
    units: Optional[str] = None
    object: Optional[Reference["Object"]] = None
    managed_object: Optional[Reference["ManagedObject"]] = None
    agent: Optional[Reference["PMAgent"]] = None
    remote_host: Optional[str] = None
    protocol: SensorProtocol = SensorProtocol.OTHER
    # Workflow state
    state: Optional[str] = None
    labels: List[str] = []
