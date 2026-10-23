# ----------------------------------------------------------------------
# SensorModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from noc.core.models.sensorprotos import SensorProtocol
from .base import BaseModel, Reference
from .object import Object
from .managedobject import ManagedObject
from .pmagent import PMAgent


class Sensor(BaseModel):
    id: str
    local_id: str
    label: str | None = None
    units: str | None = None
    object: Reference["Object"] | None = None
    managed_object: Reference["ManagedObject"] | None = None
    agent: Reference["PMAgent"] | None = None
    remote_host: str | None = None
    protocol: SensorProtocol = SensorProtocol.OTHER
    # Workflow state
    state: str | None = None
    labels: list[str] = []
