# ----------------------------------------------------------------------
# Failed Checker checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections.abc import AsyncIterable

from .base import FAIL_CHECK, SUCCESS_CHECK, BaseChecker, Check, CheckResult


class FailChecker(BaseChecker):
    """
    Stub checkers on FAIL or SUCCESS
    """

    name = "fail"
    CHECKS = [FAIL_CHECK, SUCCESS_CHECK]

    async def iter_result(self, checks: list[Check]) -> AsyncIterable[CheckResult]:
        for c in checks:
            self.logger.info("Dump check: %s", c)
            args = c.args or {}
            yield CheckResult(
                check=c.name,
                address=c.address,
                port=c.port,
                status=c.name == SUCCESS_CHECK,
                args=args,
                error=args.get("error"),
            )
