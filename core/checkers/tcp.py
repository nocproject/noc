# ----------------------------------------------------------------------
# TCP Port checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from typing import List, AsyncIterable

# NOC modules
from .base import BaseChecker, CheckResult, Check, TCP_CHECK


class TCPConnectChecker(BaseChecker):
    """
    Check address availability from remote device
    """

    name = "tcp"
    CHECKS: List[str] = [TCP_CHECK]
    SOCKET_TIMEOUT = 2

    async def iter_result(self, checks: List[Check]) -> AsyncIterable[CheckResult]:
        for c in checks:
            if not c.port:
                yield CheckResult(
                    check=TCP_CHECK,
                    port=c.port,
                    status=True,
                    skipped=True,
                )
                continue
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(c.address, c.port), self.SOCKET_TIMEOUT
                )
                writer.close()
                await writer.wait_closed()
            except (asyncio.TimeoutError, Exception):
                # реагируем на ошибку соединения, пишем в лог или ещё что
                avail = False
            else:
                # break  # соединение принято
                avail = True
                self.logger.debug("[%s] Port %s is open", c.address, c.port)
            yield CheckResult(
                check=TCP_CHECK,
                port=c.port,
                status=avail,
            )
