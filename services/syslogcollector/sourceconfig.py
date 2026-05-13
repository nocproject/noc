# ----------------------------------------------------------------------
# SourceConfig
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Tuple, Optional, List

# NOC modules
from noc.core.checkers.base import CheckResult, NODATA
from noc.config import config

TARGET_CHECK_SEND_INTERVAL = 43000


@dataclass
class RemoteSystemData(object):
    id: str
    name: str


@dataclass
class AdministrativeDomainData(object):
    id: int
    name: str
    remote_system: Optional[RemoteSystemData] = None


@dataclass
class ManagedObjectData(object):
    id: str
    bi_id: int
    name: str
    administrative_domain: AdministrativeDomainData
    labels: List[str] = None
    remote_system: Optional[RemoteSystemData] = None
    remote_id: Optional[str] = None


@dataclass
class SourceConfig(object):
    id: str
    addresses: Tuple[str, ...]
    bi_id: int
    process_events: bool
    archive_events: bool
    stream: str
    partition: int
    sa_profile: Optional[str] = None
    name: Optional[str] = None
    effective_labels: List[str] = None
    managed_object: Optional[ManagedObjectData] = None
    storm_policy: str = "D"
    storm_threshold: int = 1000
    trap_rcvd_ts: Optional[int] = None
    trap_rcvd_address: Optional[str] = None
    checks_send_ts: Optional[int] = None

    def update_rcvd(self, timestamp: int, address: str) -> bool:
        """Update source stat"""
        self.trap_rcvd_ts = timestamp
        self.trap_rcvd_address = address
        return (
            not self.checks_send_ts
            or (timestamp - self.checks_send_ts) > TARGET_CHECK_SEND_INTERVAL
        )

    def get_checks(self):
        """Getting checks"""
        self.checks_send_ts = self.trap_rcvd_ts
        return [
            CheckResult(
                check=NODATA,
                status=True,
                address=self.trap_rcvd_address,
                ttl=config.syslogcollector.target_check_ttl,
                args={"arg0": "syslogcollector", "collector": "syslogcollector"},
            )
        ]
