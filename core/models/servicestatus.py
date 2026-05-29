# ----------------------------------------------------------------------
# Service Oper Status
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from dataclasses import dataclass
from typing import Literal, Optional


class Status(enum.IntEnum):
    UNKNOWN = 0
    UP = 1
    SLIGHTLY_DEGRADED = 2
    DEGRADED = 3
    DOWN = 4


@dataclass
class AffectedItem:
    id: str
    reason: str
    service_status: Optional[Status] = None
    label: Optional[str] = None
    weight: int = 0
    is_active: bool = True
    # Add Maintenance
    source: Literal["alarm", "dependency", "diagnostic", "manual", "other"] = "other"

    @classmethod
    def from_alarm(cls, alarm, status: Status) -> "AffectedItem":
        """Build item by alarm"""
        return AffectedItem(
            service_status=status,
            id=str(alarm.id),
            reason=str(alarm.subject),
            label=alarm.body,
            source="alarm",
        )

    @classmethod
    def from_diagnostic(cls, diagnostic, status: Status) -> "AffectedItem":
        """Build item by diagnostic"""
        return AffectedItem(
            service_status=status,
            id=str(diagnostic.diagnostic),
            reason="",
            source="diagnostic",
        )

    @classmethod
    def from_dependency(cls, service, status: Status) -> "AffectedItem":
        """Build item by Service instance"""
        return AffectedItem(
            service_status=status,
            id=str(service.id),
            reason="",
            label=str(service.label),
            source="dependency",
        )
