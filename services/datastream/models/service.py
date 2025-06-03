# ----------------------------------------------------------------------
# service datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Dict

# Third-party modules
from pydantic import BaseModel

# NOC modules
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
