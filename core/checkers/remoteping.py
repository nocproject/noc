# ----------------------------------------------------------------------
# RemotePing checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable

# NOC modules
from noc.core.validators import is_ipv4
from .base import ObjectChecker, CheckResult, MetricValue
from ..wf.diagnostic import CLI_DIAG

RP_DIAG = "REMOTE_PING"


class RemotePing(ObjectChecker):
    """
    Check ManagedObject profile by rules
    """

    name = "remoteping"
    CHECKS: List[str] = [RP_DIAG]

    def iter_result(self, checks=None) -> Iterable[CheckResult]:
        if not checks:
            return
        for c in checks:
            if c.name != RP_DIAG or not c.arg0:
                continue
            for address in c.arg0.split(";"):
                if not is_ipv4(address):
                    continue
                if CLI_DIAG not in self.object.diagnostics:
                    yield CheckResult(
                        RP_DIAG, status=True, skipped=True, error="CLI Diagnostic Required"
                    )
                try:
                    r = self.object.scripts.ping(address=address)
                except AttributeError:
                    yield CheckResult(RP_DIAG, status=True, skipped=True, error="Invalid script")
                    continue
                # Remote Ping metrics
                yield CheckResult(
                    RP_DIAG,
                    status=bool(r["success"]),
                    metrics=[
                        MetricValue("Check | Status", value=int(bool(r["success"]))),
                        MetricValue("Check | Value", r["success"]),
                    ],
                )
