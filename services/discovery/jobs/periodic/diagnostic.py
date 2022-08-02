# ---------------------------------------------------------------------
# Diagnostics check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from typing import Optional, Dict, List, Union, Set
from dataclasses import dataclass

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.managedobject import ManagedObject
from noc.core.checkers.base import Checker
from noc.core.checkers.loader import loader
from noc.core.checkers.credentialchecker import CredentialChecker


@dataclass
class Metric(object):
    metric_type: str
    value: float


@dataclass
class CheckResult(object):
    name: str
    status: bool  # True - OK, False - Fail
    skipped: bool = False
    error: Optional[str] = None  # Description if Fail
    data: Optional[Union[Metric]] = None


class DiagnosticCheck(DiscoveryCheck):
    """
    Diagnostic Check discovery
    """

    name = "diagnostic"
    CHECKERS: Dict[Set[str], Checker] = {}

    def handler(self):
        object: ManagedObject = self.object
        self.CHECKERS[{c for c in CredentialChecker.CHECKS}] = CredentialChecker(self.object)
        checks: List[CheckResult] = []
        for dc in object.iter_diagnostic_configs():
            if not dc.checks or dc.blocked:
                # Diagnostic without checks
                continue
            if dc.check_policy not in {"A", "F"}:
                self.logger.info("[%s] Diagnostic for manual run. Skipping", dc.diagnostic)
                continue
            if (
                dc.check_policy == "F"
                and dc.diagnostic in self.object.diagnostics
                and self.object.diagnostics[dc.diagnostic].state == "enabled"
            ):
                self.logger.info("[%s] Diagnostic with enabled state. Skipping", dc.diagnostic)
                continue
            # Get checker
            checkers = self.get_checkers(dc.checks)
            if not checkers:
                self.logger.warning("[%s|%s] Unknown checkers. Skipping", dc.diagnostic, dc.checks)
                continue
            self.logger.info("[%s|%s] Run checker", dc.diagnostic, dc.checks)
            for c in checkers:
                c.run()
            # Cached checks
            # parse result data
        # Update diagnostics
        object.update_diagnostics(checks)
        # self.set_problem(
        #     alarm_class="Discovery | Guess | CLI Credentials",
        #     message="Failed to guess CLI credentials (%s)" % message,
        #     fatal=True,
        # )

    def get_checkers(self, checks: List[str]) -> List[Checker]:
        checks = set(checks)
        r = []
        for cc in self.CHECKERS:
            if not checks.intersection(cc):
                continue
            checks -= cc
            r += [self.CHECKERS[cc]]
            if not checks:
                break
        if checks:
            self.logger.warning("[%s] Unknown checkers. Skipping", checks)
        return r
