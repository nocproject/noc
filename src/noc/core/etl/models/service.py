# ----------------------------------------------------------------------
# ServiceModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from datetime import datetime

# Third-party modules
from pydantic import ConfigDict

# NOC modules
from .base import BaseModel, _BaseModel
from .typing import Reference, MappingItem, CapsItem
from .resourcegroup import ResourceGroup
from .serviceprofile import ServiceProfile
from .subscriber import Subscriber
from noc.core.models.serviceinstanceconfig import InstanceType, ServiceInstanceConfig


class Instance(_BaseModel):
    type: InstanceType = InstanceType.NETWORK_CHANNEL
    name: str | None = None
    # addresses: Optional[List[str]] = None
    fqdn: str | None = None
    # port: Optional[int] = None
    remote_id: str | None = None
    nri_port: str | None = None
    last_update: datetime | None = None

    @property
    def config(self) -> ServiceInstanceConfig:
        cfg = ServiceInstanceConfig.get_type(self.type)
        return cfg.from_config(
            i_type=self.type,
            name=self.name,
            remote_id=self.remote_id,
            nri_port=self.nri_port,
            fqdn=self.fqdn,
        )


class Service(BaseModel):
    id: str
    profile: Reference["ServiceProfile"]
    name_template: str | None = None
    parent: Reference["Service"] | None = None
    subscriber: Reference["Subscriber"] | None = None
    ts: datetime | None = None
    # Workflow state
    state: str | None = None
    # Last state change
    state_changed: datetime | None = None
    # Workflow event
    event: str | None = None
    agreement_id: str | None = None
    order_id: str | None = None
    stage_id: str | None = None
    stage_name: str | None = None
    stage_start: datetime | None = None
    account_id: str | None = None
    address: str | None = None
    cpe_serial: str | None = None
    cpe_mac: str | None = None
    cpe_model: str | None = None
    cpe_group: str | None = None
    labels: list[str] | None = None
    description: str | None = None
    # Groups
    static_client_groups: list[Reference["ResourceGroup"]] | None = None
    static_service_groups: list[Reference["ResourceGroup"]] | None = None
    # Custom
    capabilities: list[CapsItem] | None = None
    instances: list[Instance] | None = None
    mappings: list[MappingItem] | None = None
    checkpoint: str | None = None

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
