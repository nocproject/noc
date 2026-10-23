# ----------------------------------------------------------------------
# SourceConfig
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass

# NOC modules
from noc.core.checkers.base import CheckResult, NODATA
from noc.config import config

TARGET_CHECK_SEND_INTERVAL = 43000


@dataclass
class RemoteSystemData:
    id: str
    name: str


@dataclass
class AdministrativeDomainData:
    id: int
    name: str
    remote_system: RemoteSystemData | None = None


@dataclass
class ManagedObjectData:
    id: str
    name: str
    administrative_domain: AdministrativeDomainData
    bi_id: int | None = None
    labels: list[str] | None = None
    remote_system: RemoteSystemData | None = None
    remote_id: str | None = None


@dataclass
class SourceConfig:
    id: str
    addresses: tuple[str, ...]
    stream: str
    partition: int
    bi_id: int | None = None
    name: str | None = None
    sa_profile: str | None = None
    effective_labels: list[str] | None = None
    managed_object: ManagedObjectData | None = None
    storm_policy: str = "D"
    storm_threshold: int = 1000
    # community error
    trap_rcvd_ts: int | None = None
    trap_rcvd_address: str | None = None
    checks_send_ts: int | None = None

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
                ttl=config.trapcollector.target_check_ttl,
                args={"arg0": "trapcollector", "collector": "trapcollector"},
            )
        ]
