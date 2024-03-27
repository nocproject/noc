# ----------------------------------------------------------------------
# cfgtarget datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel


class RemoteSystem(BaseModel):
    id: str
    name: str


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
    remote_system: Optional[RemoteSystem] = None
    remote_id: Optional[str] = None


class ManagedObject(BaseModel):
    id: str
    name: str
    adm_path: List[int]
    administrative_domain: AdministrativeDomain
    remote_system: Optional[RemoteSystem] = None
    remote_id: Optional[str] = None


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


class Dependency(BaseModel):
    address: str
    name: str
    settings: PingSettings


class CfgTarget(BaseModel):
    id: str  # Record id
    name: str
    addresses: List[TargetAddress]
    opaque_data: Optional[ManagedObject]  # Kafka message data
    effective_labels: List[str]
    bi_id: int
    pool: str
    fm_pool: Optional[str] = None
    process_events: bool = True
    ping: Optional[PingSettings] = None
    syslog: Optional[SyslogSettings] = None
    trap: Optional[TrapSettings] = None
    dependencies: Optional[List[Dependency]] = None
