# ---------------------------------------------------------------------
# Diagnostics check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from typing import Optional, Dict, List, Union, Set
from dataclasses import dataclass
from collections import defaultdict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.checkers.base import Checker, Check
from noc.core.checkers.loader import loader


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
    CHECKERS: Dict[str, Checker] = {}  # Checkers Instance
    CHECK_MAP: Dict[str, str] = {}  # CheckName -> CheckerName mapping

    CHECK_CACHE = {}  # Cache cache

    def load_checkers(self):
        """
        Load available checkers
        :return:
        """
        for checker in loader:
            self.CHECKERS[checker] = loader[checker](self.object)
            for c in self.CHECKERS[checker].CHECKS:
                self.CHECK_MAP[c] = self.CHECKERS[checker].name

    def handler(self):
        self.load_checkers()
        checks: List[CheckResult] = []
        # configs: Dict[str, DiagnosticConfig] = {}
        for dc in self.object.iter_diagnostic_configs():
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
            checks += self.do_check(dc.checks)
        self.logger.info("Result: %s", checks)
        # Processed Check

        # Update diagnostics
        # object.update_diagnostics([CheckData(name=cr.name, status=cr.status, skipped=cr.skipped, error=cr.error) for cr in checks])
        # self.set_problem(
        #     alarm_class="Discovery | Guess | CLI Credentials",
        #     message="Failed to guess CLI credentials (%s)" % message,
        #     fatal=True,
        # )

    def do_check(self, checks: List[Check]) -> List[CheckResult]:
        """
        Run checks on Checker
        :param checks:
        :return:
        """
        r = []
        # Group check by checker
        do_checks: Dict[str, List[Check]] = defaultdict(list)
        for c in checks:
            if c.name not in self.CHECK_MAP:
                self.logger.warning("[%s] Unknown check. Skipping", c.name)
                continue
            if c in self.CHECK_CACHE:
                r.append(self.CHECK_CACHE[c])
                continue
            do_checks[self.CHECK_MAP[c.name]] += [Check]

        for checker, d_checks in do_checks.items():
            checker = self.CHECKERS[checker]
            self.logger.info("[%s] Run checker", d_checks)
            r += checker.run(d_checks)
        return r
