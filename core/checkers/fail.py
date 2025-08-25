# ----------------------------------------------------------------------
# Failed Checker checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, AsyncIterable

# NOC modules
from .base import BaseChecker, CheckResult, Check, FAIL_CHECK


class FailChecker(BaseChecker):
    """
    Check address availability from remote device
    """

    name = "fail"
    CHECKS: List[str] = [FAIL_CHECK]
    SOCKET_TIMEOUT = 2

    async def iter_result(self, checks: List[Check]) -> AsyncIterable[CheckResult]:
        for c in checks:
            self.logger.info("Dump check: %s", c)
            if c.args.get("status") == "ok":
                yield CheckResult(
                    check=FAIL_CHECK,
                    address=c.address,
                    port=c.port,
                    status=True,
                    args=c.args,
                )
            else:
                yield CheckResult(
                    check=FAIL_CHECK,
                    address=c.address,
                    port=c.port,
                    status=False,
                    args=c.args,
                    error=c.args.get("error"),
                )
