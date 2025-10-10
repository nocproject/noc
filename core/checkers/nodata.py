# ----------------------------------------------------------------------
# NoData Checker checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, AsyncIterable

# NOC modules
from .base import BaseChecker, CheckResult, Check, NODATA


class NoDataChecker(BaseChecker):
    """
    Check address availability from remote device
    """

    name = "nodata"
    CHECKS: List[str] = [NODATA]

    async def iter_result(self, checks: List[Check]) -> AsyncIterable[CheckResult]:
        for c in checks:
            self.logger.info("Dump check: %s", c)
            yield CheckResult(
                check=NODATA,
                address=c.address,
                port=c.port,
                status=True,
                args=c.args,
            )
