# ----------------------------------------------------------------------
# SourceConfig
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Tuple, Optional, List

# NOC modules
from noc.core.checkers.base import CheckResult, NODATA


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
    name: str
    administrative_domain: AdministrativeDomainData
    bi_id: int = None
    labels: List[str] = None
    remote_system: Optional[RemoteSystemData] = None
    remote_id: Optional[str] = None


@dataclass
class SourceConfig(object):
    id: str
    addresses: Tuple[str, ...]
    stream: str
    partition: int
    bi_id: Optional[int] = None
    name: Optional[str] = None
    sa_profile: Optional[str] = None
    effective_labels: List[str] = None
    managed_object: Optional[ManagedObjectData] = None
    storm_policy: str = "D"
    storm_threshold: int = 1000
    # community error
    trap_rcvd_ts: Optional[int] = None
    trap_rcvd_address: Optional[str] = None
    checks_send_ts: Optional[int] = None

    def update_rcvd(self, timestamp: int, address: str) -> bool:
        """Update source stat"""
        self.trap_rcvd_ts = timestamp
        self.trap_rcvd_address = address
        return not self.checks_send_ts or (timestamp - self.checks_send_ts) > 3600

    def get_checks(self):
        """Getting checks"""
        self.checks_send_ts = self.trap_rcvd_ts
        return [
            CheckResult(
                check=NODATA,
                status=True,
                address=self.trap_rcvd_address,
                ttl=1800,
                args={"arg0": "trapcollector", "collector": "trapcollector"},
            )
        ]
