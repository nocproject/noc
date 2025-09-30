# ----------------------------------------------------------------------
# Send Metric Request
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from dataclasses import dataclass
from typing import Any, Optional, List, Dict


@dataclass
class SendMetric:
    ts: datetime.datetime
    managed_object: int
    collector: str
    metrics: Dict[str, Any]
    labels: Optional[List[str]] = None
    service: Optional[int] = None
    remote_system: Optional[str] = None

    @property
    def key(self) -> int:
        if self.managed_object:
            return self.managed_object
        elif self.service:
            return self.service
        return 0
