# ---------------------------------------------------------------------
# Diagnostics check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict, List
from collections import defaultdict

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.core.checkers.base import (
    Checker,
    Check,
    CheckResult,
    ProfileSet,
    CredentialSet,
    MetricsSet,
)
from noc.core.checkers.loader import loader
from noc.sa.models.managedobject import CheckData
from noc.sa.models.profile import Profile


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
        # Processed Check
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
            for cc in self.do_check([Check(name=dc) for dc in dc.checks]):
                if cc.action and not hasattr(self, cc.action.action):
                    self.logger.warning(
                        "[%s|%s] Unknown action", dc.diagnostic, cc.check, cc.action.action
                    )
                elif cc.action:
                    h = getattr(self, f"action_{cc.action.action}")
                    h(cc.action)
                checks.append(cc)
        self.logger.info("Result: %s", checks)
        # Update diagnostics
        self.object.update_diagnostics(
            [
                CheckData(name=cr.check, status=cr.status, skipped=cr.skipped, error=cr.error)
                for cr in checks
            ]
        )
        # Fire workflow event diagnostic ?

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
            do_checks[self.CHECK_MAP[c.name]] += [c]

        for checker, d_checks in do_checks.items():
            checker = self.CHECKERS[checker]
            self.logger.info("[%s] Run checker", d_checks)
            r += checker.run(d_checks)
        return r

    def action_set_sa_profile(self, data: ProfileSet):
        """
        Setting Object Profile Check result
        :param data:
        :return:
        """
        # if "profile" not in data:
        #     return  # Cannot detect
        profile = Profile.get_by_name(data.profile)
        if profile.id == self.object.profile.id:
            self.logger.info("Profile is correct: %s", profile)
        else:
            self.logger.info(
                "Profile change detected: %s -> %s. Fixing database, resetting platform info",
                self.object.profile.name,
                profile.name,
            )
            self.invalidate_neighbor_cache()
            self.object.profile = profile
            self.object.vendor = None
            self.object.plarform = None
            self.object.version = None
            self.object.save()

    def action_set_credential(self, data: CredentialSet):
        """
        :param data:
        :return:
        """
        changed = False
        for cred in ["snmp_ro", "snmp_rw", "user", "password", "super_password"]:
            nc = getattr(data, cred)
            if not nc:
                continue
            oc = getattr(self.object, cred, None)
            if nc != oc:
                changed = True
                setattr(self.object, cred, nc)
        # Reset auth profile to continue operations with new credentials
        if changed:
            self.logger.info("Setting credentials")
            self.object.auth_profile = None
            self.object.save()

    def action_set_metrics(self, data: MetricsSet):
        """
        Register Diagnostic Metrics
        :param data:
        :return:
        """
        self.logger.info("Register metric: %s", data)
