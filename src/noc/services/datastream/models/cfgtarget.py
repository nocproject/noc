# ----------------------------------------------------------------------
# cfgtarget datastream model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel

# NOC Modules
from .utils import ManagedObjectOpaque


class TargetAddress(BaseModel):
    address: str  # IP address
    is_fatal: bool = False  # Address used for NOC access
    interface: str | None = None  # Assigned Interface name
    syslog_source: bool = True
    trap_source: bool = True
    ping_check: bool = False


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


class CfgTarget(BaseModel):
    id: str  # Record id
    name: str
    addresses: list[TargetAddress]
    bi_id: int
    pool: str
    effective_labels: list[str]
    opaque_data: ManagedObjectOpaque | None = None  # Kafka message data
    sa_profile: str | None = None
    fm_pool: str | None = None
    process_events: bool = True
    ping: PingSettings | None = None
    syslog: SyslogSettings | None = None
    trap: TrapSettings | None = None
    # checks: Optional[List[CheckConfig]] = None
    services: list[dict[str, str]] | None = None
    dependencies: list[Dependency] | None = None
    mapping_refs: list[str] | None = None
    watchers: list[str] | None = None
