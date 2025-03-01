# ----------------------------------------------------------------------
# TCP Port checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import socket
import asyncio
from typing import List, Iterable

# NOC modules
from .base import Checker, CheckResult, Check

TCP_DIAG = "TCP"


class TCPConnect(Checker):
    """
    Check address availability from remote device
    """

    name = "tcp"
    CHECKS: List[str] = [TCP_DIAG]
    SOCKET_TIMEOUT = 2

    async def iter_result_async(self, checks: List[Check]) -> Iterable[CheckResult]:
        for c in checks:
            if not c.port:
                yield CheckResult(
                    check=TCP_DIAG,
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
                check=TCP_DIAG,
                port=c.port,
                status=avail,
            )

    def iter_result(self, checks: List[Check]) -> Iterable[CheckResult]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self.SOCKET_TIMEOUT)
            # sock.setblocking(False)
            for c in checks:
                if not c.port:
                    yield CheckResult(
                        check=TCP_DIAG,
                        port=c.port,
                        status=True,
                        skipped=True,
                    )
                    continue
                if sock.connect_ex((c.address, c.port)) == 0:
                    self.logger.debug("[%s] Port %s is open", c.address, c.port)
                    avail = True
                else:
                    avail = False
                yield CheckResult(
                    check=TCP_DIAG,
                    port=c.port,
                    status=avail,
                )
