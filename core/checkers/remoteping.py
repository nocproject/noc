# ----------------------------------------------------------------------
# RemotePing checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable

# NOC modules
from .base import Checker, CheckResult, MetricValue, CheckError
from noc.core.wf.diagnostic import CLI_DIAG
from noc.core.validators import is_ipv4

RP_DIAG = "REMOTE_PING"


class RemotePing(Checker):
    """
    Check address availability from remote device
    """

    name = "remoteping"
    CHECKS: List[str] = [RP_DIAG]
    REQUIRED_DIAGS: List[str] = [CLI_DIAG]

    def iter_result(self, checks=None) -> Iterable[CheckResult]:
        if not checks:
            return
        for c in checks:
            if c.name != RP_DIAG or not c.arg0:
                continue
            if not is_ipv4(c.address):
                continue
            try:
                ping = self.get_script("ping")
                r = ping(address=c.address)
            except AttributeError:
                yield CheckResult(
                    RP_DIAG,
                    status=True,
                    skipped=True,
                    error=CheckError(code="0", message="Invalid script"),
                )
                continue
            # Remote Ping metrics
            yield CheckResult(
                RP_DIAG,
                status=bool(r["success"]),
                address=c.address,
                metrics=[
                    MetricValue(
                        "Check | Result",
                        r["success"],
                        labels=[
                            f"noc::check::name::{c.name}",
                            f"noc::check::arg0::{c.arg0}",
                        ],
                    )
                ],
            )
