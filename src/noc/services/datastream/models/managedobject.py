# ----------------------------------------------------------------------
# managedobject datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import annotations
import datetime
from typing import Any

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
    remote_system: RemoteSystemItem | None
    remote_id: str | None


class ProjectItem(BaseModel):
    code: str
    name: str
    remote_system: RemoteSystemItem | None
    remote_id: str | None


class AdministrativeDomainItem(BaseModel):
    id: str
    name: str
    remote_system: RemoteSystemItem | None
    remote_id: str | None


class ObjectProfileItem(BaseModel):
    id: str
    name: str
    level: int
    enable_ping: bool
    enable_box: bool
    enable_periodic: bool
    labels: list[str] | None
    tags: list[str] | None
    remote_system: RemoteSystemItem | None
    remote_id: str | None


class ChassisMACItem(BaseModel):
    first: str
    last: str


class ChassisIDItem(BaseModel):
    hostname: str | None
    macs: list[ChassisMACItem] | None
    router_id: str | None
    udld_id: str | None


class ForwardingInstanceItem(BaseModel):
    name: str
    type: str
    subinterfaces: list[str]
    rd: str | None
    vpn_id: str | None
    rt_export: str | None
    rt_import: str | None


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
    enabled_afi: list[str]
    enabled_protocols: list[str]
    snmp_ifindex: int | None
    mac: str | None
    ipv4_addresses: list[str] | None
    ipv6_addresses: list[str] | None
    iso_addresses: list[str] | None
    vlan_ids: list[str] | None
    vpi: str | None
    vci: str | None
    untagged_vlan: int | None
    tagged_vlans: list[int] | None


class LinkItem(BaseModel):
    object: str
    interface: str
    method: str
    is_uplink: bool


class InterfaceItem(BaseModel):
    name: str
    type: str
    description: str
    enabled_protocols: list[str]
    admin_status: bool
    hints: list[str]
    snmp_ifindex: int | None
    mac: str | None
    aggregated_interface: str | None
    profile: InterfaceProfileItem | None
    subinterfaces: list[SubinterfaceItem]
    link: list[LinkItem]


class VendorItem(BaseModel):
    id: str
    name: str


class ModelItem(BaseModel):
    id: str
    name: str
    description: str | None
    vendor: VendorItem
    labels: list[str] | None
    tags: list[str] | None


class SlotItem(BaseModel):
    name: str
    direction: str
    protocols: list[str]
    asset: Any | None
    interface: str | None


class AssetItem(BaseModel):
    id: str
    model: ModelItem
    serial: str
    revision: str
    data: dict[str, dict[str, str | int | bool]]
    slots: list[SlotItem]


class ConfigItem(BaseModel):
    revision: str
    size: str
    updated: datetime.datetime


class ManagedObjectDataStreamItem(BaseModel):
    id: str
    change_id: str
    name: str
    bi_id: int
    profile: str
    is_managed: bool
    address: str | None
    description: str | None
    labels: list[str] | None
    tags: list[str] | None
    project: ProjectItem | None
    remote_system: RemoteSystemItem | None
    remote_id: str | None
    pool: str | None
    vendor: str | None
    platform: str | None
    version: str | None
    capabilities: list[CapabilitiesItem] | None
    segment: SegmentItem | None
    administrative_domain: AdministrativeDomainItem | None
    object_profile: ObjectProfileItem
    chassis_id: ChassisIDItem | None
    forwarding_instances: list[ForwardingInstanceItem] | None
    interfaces: list[InterfaceItem]
    service_groups: list[ResourceGroupItem] | None
    client_groups: list[ResourceGroupItem] | None
    asset: list[AssetItem] | None
    config: list[ConfigItem] | None
