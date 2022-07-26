# ----------------------------------------------------------------------
# ServiceModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Union
from datetime import datetime

# NOC modules
from .base import BaseModel, _BaseModel
from .typing import Reference
from .serviceprofile import ServiceProfile
from .managedobject import ManagedObject
from .subscriber import Subscriber


class CapsItem(_BaseModel):
    name: str
    value: Union[str, bool, int]


class Service(BaseModel):
    id: str
    parent: Optional[Reference["Service"]]
    subscriber: Optional[Reference["Subscriber"]]
    profile: Reference["ServiceProfile"]
    ts: Optional[datetime]
    # Workflow state
    state: Optional[str]
    # Last state change
    state_changed: Optional[datetime]
    # Workflow event
    event: Optional[str]
    agreement_id: Optional[str]
    order_id: Optional[str]
    stage_id: Optional[str]
    stage_name: Optional[str]
    stage_start: Optional[datetime]
    account_id: Optional[str]
    address: Optional[str]
    managed_object: Optional[Reference["ManagedObject"]]
    nri_port: Optional[str]
    cpe_serial: Optional[str]
    cpe_mac: Optional[str]
    cpe_model: Optional[str]
    cpe_group: Optional[str]
    labels: Optional[List[str]]
    description: Optional[str] = None
    capabilities: Optional[List[CapsItem]]
    checkpoint: Optional[str]

    class Config:
        fields = {"state_changed": "logical_status_start", "state": "logical_status"}
        allow_population_by_field_name = True

    _csv_fields = [
        "id",
        "parent",
        "subscriber",
        "profile",
        "ts",
        "state",
        "state_changed",
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
        "labels",
    ]
