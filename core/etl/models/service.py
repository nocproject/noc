# ----------------------------------------------------------------------
# ServiceModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel
from .typing import Reference
from .serviceprofile import ServiceProfile
from .managedobject import ManagedObject
from .subscriber import Subscriber


class Service(BaseModel):
    id: str
    parent: Optional[Reference["Service"]]
    subscriber: Reference["Subscriber"]
    profile: Reference["ServiceProfile"]
    ts: str
    logical_status: str
    logical_status_start: str
    agreement_id: Optional[str]
    order_id: Optional[str]
    stage_id: Optional[str]
    stage_name: Optional[str]
    stage_start: Optional[str]
    account_id: Optional[str]
    address: Optional[str]
    managed_object: Optional[Reference["ManagedObject"]]
    nri_port: Optional[str]
    cpe_serial: Optional[str]
    cpe_mac: Optional[str]
    cpe_model: Optional[str]
    cpe_group: Optional[str]
    description: Optional[str]

    _csv_fields = [
        "id",
        "parent",
        "subscriber",
        "profile",
        "ts",
        "logical_status",
        "logical_status_start",
        "agreement_id",
        "order_id",
        "stage_id",
        "stage_name",
        "stage_start",
        "account_id",
        "address",
        "managed_object",
        "nri_port",
        "cpe_serial",
        "cpe_mac",
        "cpe_model",
        "cpe_group",
        "description",
    ]
