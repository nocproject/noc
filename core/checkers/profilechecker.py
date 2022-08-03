# ----------------------------------------------------------------------
# Profile checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List

# NOC modules
from .base import Check, ObjectChecker, CheckResult, ProfileSet
from ..profile.checker import ProfileChecker as ProfileCheckerProfile
from ..script.credentialchecker import Protocol
from ..wf.diagnostic import DiagnosticState, SNMP_DIAG


class ProfileChecker(ObjectChecker):
    name = "profile"
    CHECKS: List[str] = ["PROFILE"]
    CHECK_SNMP_VERSION_MAP = {
        p.config.check: p.config.snmp_version
        for p in Protocol
        if p.config.snmp_version and p.config.check
    }

    def run(self, checks: List[Check]) -> List[CheckResult]:
        """
        :param checks:
        :return:
        """
        snmp_community, snmp_version = None, []
        if (
            SNMP_DIAG in self.object.diagnostics
            and self.object.diagnostics[SNMP_DIAG] == DiagnosticState.enabled
        ):
            snmp_community = self.object.credentials.snmp_ro
            snmp_version = [
                self.CHECK_SNMP_VERSION_MAP[check]
                for check in self.object.diagnostics[SNMP_DIAG]["checks"]
            ]
        # caps = self.object.get_caps()
        # if caps.get("SNMP | v2c") is False or caps.get("SNMP | v2c") is None:
        #     snmp_version = [SNMP_v1, SNMP_v2c]
        # else:
        #     snmp_version = [SNMP_v2c, SNMP_v1]
        #
        checker = ProfileCheckerProfile(
            self.object.address,
            self.object.pool.name,
            logger=self.logger,
            calling_service="discovery",
            snmp_community=snmp_community,
            snmp_version=snmp_version,
        )
        profile = checker.get_profile()
        if not profile:
            return [CheckResult(check="PROFILE", status=bool(profile), error=checker.get_error())]
        # Skipped
        return [
            CheckResult(
                check="PROFILE",
                status=bool(profile),
                data={"profile": profile.name},
                action=ProfileSet(profile=profile.name),
            )
        ]
