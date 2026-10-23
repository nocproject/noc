# ----------------------------------------------------------------------
# service datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Literal

# Third-party modules
from pydantic import BaseModel

# NOC modules
from noc.core.models.serviceinstanceconfig import InstanceType
from .utils import StateItem, ProjectItem, RemoteSystemItem, RemoteMapItem


class CapabilitiesItem(BaseModel):
    name: str
    value: str


class ServiceProfileItem(BaseModel):
    id: str
    name: str


class ResourceGroupItem(BaseModel):
    id: str
    name: str
    technology: str
    static: bool


class ServiceItem(BaseModel):
    id: str
    label: str
    remote_system: RemoteSystemItem | None
    remote_id: str | None


class Dependency(BaseModel):
    service: ServiceItem
    method: Literal["parent", "used_by"] = "parent"
    status_affected: bool = False
    status_direction: Literal["in", "out", "both"] | None = None
    # direction: Optional[Literal["in", "out", "top", "down", "used"]]


class ServiceInstanceItem(BaseModel):
    id: str
    type: InstanceType
    name: str | None
    fqdn: str | None
    managed_object: str | None
    remote_system: RemoteSystemItem | None
    remote_id: str | None


class ServiceDataStreamItem(BaseModel):
    id: str
    change_id: str
    label: str
    bi_id: int
    state: StateItem
    parent: str | None
    profile: ServiceProfileItem
    description: str | None
    labels: list[str] | None
    agreement_id: str | None
    address: str | None
    capabilities: list[CapabilitiesItem] | None
    project: ProjectItem | None
    remote_system: RemoteSystemItem | None
    service_groups: list[ResourceGroupItem] | None
    client_groups: list[ResourceGroupItem] | None
    remote_mappings: list[RemoteMapItem] | None
    effective_remote_map: dict[str, str] | None
    instances: list[ServiceInstanceItem] | None
    dependencies: list[Dependency] | None
