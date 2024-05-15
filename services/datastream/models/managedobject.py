# ----------------------------------------------------------------------
# managedobject datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import annotations
import datetime
from typing import Optional, List, Dict, Union, Any

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import RemoteSystemItem


class CapabilitiesItem(BaseModel):
    name: str
    value: str


class SegmentItem(BaseModel):
    id: str
    name: str
    remote_system: Optional[RemoteSystemItem]
    remote_id: Optional[str]


class ProjectItem(BaseModel):
    code: str
    name: str
    remote_system: Optional[RemoteSystemItem]
    remote_id: Optional[str]


class AdministrativeDomainItem(BaseModel):
    id: str
    name: str
    remote_system: Optional[RemoteSystemItem]
    remote_id: Optional[str]


class ObjectProfileItem(BaseModel):
    id: str
    name: str
    level: int
    enable_ping: bool
    enable_box: bool
    enable_periodic: bool
    labels: Optional[List[str]]
    tags: Optional[List[str]]
    remote_system: Optional[RemoteSystemItem]
    remote_id: Optional[str]


class ChassisMACItem(BaseModel):
    first: str
    last: str


class ChassisIDItem(BaseModel):
    hostname: Optional[str]
    macs: Optional[List[ChassisMACItem]]
    router_id: Optional[str]
    udld_id: Optional[str]


class ForwardingInstanceItem(BaseModel):
    name: str
    type: str
    subinterfaces: List[str]
    rd: Optional[str]
    vpn_id: Optional[str]
    rt_export: Optional[str]
    rt_import: Optional[str]


class ResourceGroupItem(BaseModel):
    id: str
    name: str
    technology: str
    static: bool


class InterfaceProfileItem(BaseModel):
    id: str
    name: str


class SubinterfaceItem(BaseModel):
    name: str
    description: str
    enabled_afi: List[str]
    enabled_protocols: List[str]
    snmp_ifindex: Optional[int]
    mac: Optional[str]
    ipv4_addresses: Optional[List[str]]
    ipv6_addresses: Optional[List[str]]
    iso_addresses: Optional[List[str]]
    vlan_ids: Optional[List[str]]
    vpi: Optional[str]
    vci: Optional[str]
    untagged_vlan: Optional[int]
    tagged_vlans: Optional[List[int]]


class LinkItem(BaseModel):
    object: str
    interface: str
    method: str
    is_uplink: bool


class InterfaceItem(BaseModel):
    name: str
    type: str
    description: str
    enabled_protocols: List[str]
    admin_status: bool
    hints: List[str]
    snmp_ifindex: Optional[int]
    mac: Optional[str]
    aggregated_interface: Optional[str]
    profile: Optional[InterfaceProfileItem]
    subinterfaces: List[SubinterfaceItem]
    link: List[LinkItem]


class VendorItem(BaseModel):
    id: str
    name: str


class ModelItem(BaseModel):
    id: str
    name: str
    description: Optional[str]
    vendor: VendorItem
    labels: Optional[List[str]]
    tags: Optional[List[str]]


class SlotItem(BaseModel):
    name: str
    direction: str
    protocols: List[str]
    asset: Optional[Any]
    interface: Optional[str]


class AssetItem(BaseModel):
    id: str
    model: ModelItem
    serial: str
    revision: str
    data: Dict[str, Dict[str, Union[str, int, bool]]]
    slots: List[SlotItem]


class ConfigItem(BaseModel):
    revision: str
    size: str
    updated: datetime.datetime


class ManagedObjectDataStreamItem(BaseModel):
    id: str
    change_id: str
    name: str
    version: int
    bi_id: int
    profile: str
    is_managed: bool
    address: Optional[str]
    description: Optional[str]
    labels: Optional[List[str]]
    tags: Optional[List[str]]
    project: Optional[ProjectItem]
    remote_system: Optional[RemoteSystemItem]
    remote_id: Optional[str]
    pool: Optional[str]
    vendor: Optional[str]
    platform: Optional[str]
    version: Optional[str]
    capabilities: Optional[List[CapabilitiesItem]]
    segment: Optional[SegmentItem]
    administrative_domain: Optional[AdministrativeDomainItem]
    object_profile: ObjectProfileItem
    chassis_id: Optional[ChassisIDItem]
    forwarding_instances: Optional[List[ForwardingInstanceItem]]
    interfaces: List[InterfaceItem]
    service_groups: Optional[List[ResourceGroupItem]]
    client_groups: Optional[List[ResourceGroupItem]]
    asset: Optional[List[AssetItem]]
    config: Optional[List[ConfigItem]]
