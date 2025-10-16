# ----------------------------------------------------------------------
# cfgtarget datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel

# NOC Modules
from .utils import RemoteMapItem, RemoteSystemItem


class TargetAddress(BaseModel):
    address: str  # IP address
    is_fatal: bool = False  # Address used for NOC access
    interface: Optional[str] = None  # Assigned Interface name
    syslog_source: bool = True
    trap_source: bool = True
    ping_check: bool = False


class AdministrativeDomain(BaseModel):
    id: str
    name: str
    remote_system: Optional[RemoteSystemItem] = None
    remote_id: Optional[str] = None


class Service(BaseModel):
    id: str
    bi_id: str


class ManagedObject(BaseModel):
    id: str
    name: str
    adm_path: List[int]
    administrative_domain: AdministrativeDomain
    remote_system: Optional[RemoteSystemItem] = None
    remote_id: Optional[str] = None
    mappings: Optional[List[RemoteMapItem]] = None
    services: Optional[List[Service]] = None


class PingSettings(BaseModel):
    interval: int
    policy: str
    size: int
    count: int
    timeout: int
    expr_policy: str
    report_rtt: bool = False
    report_attempts: bool = False


class TrapSettings(BaseModel):
    community: str
    storm_policy: str
    storm_threshold: int


class SyslogSettings(BaseModel):
    archive_events: bool = False
    storm_policy: str
    storm_threshold: int


class Dependency(BaseModel):
    address: str
    name: str
    settings: PingSettings


class MetricCollectorSettings(BaseModel):
    name: str
    api_key: str
    bi_id: Optional[int] = None
    enable_fmevent: bool = True
    enable_metrics: bool = False
    nodata_policy: str = "D"
    nodata_ttl: Optional[int] = None
    # register_unknown_policy
    remote_system: Optional[str] = None
    allowed_addresses: Optional[List[str]] = None


class CfgTarget(BaseModel):
    id: str  # Record id
    name: str
    addresses: List[TargetAddress]
    bi_id: int
    pool: str
    effective_labels: List[str]
    opaque_data: Optional[ManagedObject] = None  # Kafka message data
    sa_profile: Optional[str] = None
    fm_pool: Optional[str] = None
    process_events: bool = True
    ping: Optional[PingSettings] = None
    syslog: Optional[SyslogSettings] = None
    trap: Optional[TrapSettings] = None
    metric: Optional[List[MetricCollectorSettings]] = None
    # checks: Optional[List[CheckConfig]] = None
    dependencies: Optional[List[Dependency]] = None
    mapping_refs: Optional[List[str]] = None
    watchers: Optional[List[str]] = None
