# ----------------------------------------------------------------------
# ServiceModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List
from datetime import datetime

# Third-party modules
from pydantic import ConfigDict

# NOC modules
from .base import BaseModel, _BaseModel
from .typing import Reference, MappingItem, CapsItem
from .serviceprofile import ServiceProfile
from .subscriber import Subscriber
from noc.core.models.serviceinstanceconfig import InstanceType


class Instance(_BaseModel):
    type: InstanceType = InstanceType.NETWORK_CHANNEL
    name: Optional[str] = None
    addresses: Optional[List[str]] = None
    fqdn: Optional[str] = None
    port: Optional[int] = None
    remote_id: Optional[str] = None
    nri_port: Optional[str] = None
    mac_addresses: Optional[List[str]] = None
    last_update: Optional[datetime] = None


class Service(BaseModel):
    id: str
    profile: Reference["ServiceProfile"]
    name_template: Optional[str] = None
    parent: Optional[Reference["Service"]] = None
    subscriber: Optional[Reference["Subscriber"]] = None
    ts: Optional[datetime] = None
    # Workflow state
    state: Optional[str] = None
    # Last state change
    state_changed: Optional[datetime] = None
    # Workflow event
    event: Optional[str] = None
    agreement_id: Optional[str] = None
    order_id: Optional[str] = None
    stage_id: Optional[str] = None
    stage_name: Optional[str] = None
    stage_start: Optional[datetime] = None
    account_id: Optional[str] = None
    address: Optional[str] = None
    cpe_serial: Optional[str] = None
    cpe_mac: Optional[str] = None
    cpe_model: Optional[str] = None
    cpe_group: Optional[str] = None
    labels: Optional[List[str]] = None
    description: Optional[str] = None
    capabilities: Optional[List[CapsItem]] = None
    instances: Optional[List[Instance]] = None
    mappings: Optional[List[MappingItem]] = None
    checkpoint: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

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
