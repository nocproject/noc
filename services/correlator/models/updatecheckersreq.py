# ---------------------------------------------------------------------
# SetDiagnosticStatus Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, Literal, List, Dict

# Third-party modules
from pydantic import BaseModel, Field

# NOC modules
from noc.core.checkers.base import CheckResult


class CheckResultItem(BaseModel):
    check: str
    status: bool
    args: Optional[Dict[str, str]] = None
    port: Optional[int] = None
    address: Optional[str] = None
    skipped: bool = False
    error: Optional[str] = None
    timestamp: Optional[datetime.datetime] = None

    def get_result(self) -> CheckResult:
        return CheckResult(
            check=self.check,
            status=self.status,
            args=self.args,
            port=self.port,
            address=self.address,
            skipped=self.skipped,
            error=self.error,
        )


class ObjectResult(BaseModel):
    id: str
    target_type: Literal["managed_object", "service"] = "managed_object"
    statuses: List[CheckResultItem]


class UpdateCheckersRequest(BaseModel):
    op: Literal["update_checkers_status"] = Field(None, alias="$op")
    results: List[ObjectResult]
