# ----------------------------------------------------------------------
# service datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict, Literal

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
    remote_system: Optional[RemoteSystemItem]
    remote_id: Optional[str]


class Dependency(BaseModel):
    service: ServiceItem
    method: Literal["parent", "used_by"] = "parent"
    status_affected: bool = False
    status_direction: Optional[Literal["in", "out", "both"]] = None
    # direction: Optional[Literal["in", "out", "top", "down", "used"]]


class ServiceInstanceItem(BaseModel):
    id: str
    type: InstanceType
    name: Optional[str]
    fqdn: Optional[str]
    managed_object: Optional[str]
    remote_system: Optional[RemoteSystemItem]
    remote_id: Optional[str]


class ServiceDataStreamItem(BaseModel):
    id: str
    change_id: str
    label: str
    bi_id: int
    state: StateItem
    parent: Optional[str]
    profile: ServiceProfileItem
    description: Optional[str]
    labels: Optional[List[str]]
    agreement_id: Optional[str]
    address: Optional[str]
    capabilities: Optional[List[CapabilitiesItem]]
    project: Optional[ProjectItem]
    remote_system: Optional[RemoteSystemItem]
    service_groups: Optional[List[ResourceGroupItem]]
    client_groups: Optional[List[ResourceGroupItem]]
    remote_mappings: Optional[List[RemoteMapItem]]
    effective_remote_map: Optional[Dict[str, str]]
    instances: Optional[List[ServiceInstanceItem]]
    dependencies: Optional[List[Dependency]]
