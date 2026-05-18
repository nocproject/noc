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
class StatusAffectedItem:
    status: Status
    id: str
    reason: str
    label: Optional[str] = None
    weight: int = 0
    source: Literal["alarm", "dependency", "diagnostic", "manual", "other"] = "other"

    @classmethod
    def from_alarm(cls, alarm, status: Status) -> "StatusAffectedItem":
        """Build item by alarm"""
        return StatusAffectedItem(
            status=status,
            id=str(alarm.id),
            reason=str(alarm.subject),
            label=alarm.body,
            source="alarm",
        )

    @classmethod
    def from_diagnostic(cls, diagnostic, status: Status) -> "StatusAffectedItem":
        """Build item by diagnostic"""
        return StatusAffectedItem(
            status=status,
            id=str(diagnostic.diagnostic),
            reason="",
            source="diagnostic",
        )

    @classmethod
    def from_dependency(cls, service, status: Status) -> "StatusAffectedItem":
        """Build item by Service instance"""
        return StatusAffectedItem(
            status=status,
            id=str(service.id),
            reason="",
            label=str(service.label),
            source="dependency",
        )
