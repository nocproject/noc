# ----------------------------------------------------------------------
# TCP Port checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import socket
from typing import List, Iterable

# NOC modules
from .base import Checker, CheckResult

TCP_DIAG = "TCP"


class TCPConnect(Checker):
    """
    Check address availability from remote device
    """

    name = "tcp"
    CHECKS: List[str] = [TCP_DIAG]
    SOCKET_TIMEOUT = 2

    def iter_result(self, checks) -> Iterable[CheckResult]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self.SOCKET_TIMEOUT)
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
