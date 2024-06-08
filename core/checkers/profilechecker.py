# ----------------------------------------------------------------------
# Profile checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable

# NOC modules
from noc.core.text import filter_non_printable
from noc.core.snmp.version import SNMP_v1, SNMP_v2c
from .base import Checker, CheckResult, DataItem, CheckError
from ..profile.checker import ProfileChecker as ProfileCheckerProfile


class ProfileChecker(Checker):
    """
    Check ManagedObject profile by rules
    """

    name = "profilechecker"
    CHECKS: List[str] = []
    USER_DISCOVERY_USE = False

    def iter_result(self, checks) -> Iterable[CheckResult]:
        check = checks[0]
        snmp_community, snmp_version = None, []
        if check.snmp_credential:
            snmp_community = check.snmp_credential.snmp_ro
            if check.snmp_credential.snmp_v1_only:
                snmp_version = [SNMP_v1]
            else:
                snmp_version = [SNMP_v2c, SNMP_v1]
        checker = ProfileCheckerProfile(
            check.address,
            self.pool,
            logger=self.logger,
            calling_service=self.calling_service,
            snmp_community=snmp_community,
            snmp_version=snmp_version,
        )
        profile = checker.get_profile()
        if profile:
            # Skipped
            yield CheckResult(
                check="PROFILE",
                status=bool(profile),
                data=[DataItem(name="profile", value=profile.name)],
            )
            return
        yield CheckResult(
            check="PROFILE",
            status=bool(profile),
            error=CheckError(code="0", message=filter_non_printable(checker.get_error())[:200]),
        )
        # If check SNMP failed - Set SNMP error
        if not checker.ignoring_snmp and checker.snmp_check is False:
            for sv in snmp_version:
                yield CheckResult(
                    check={SNMP_v1: "SNMPv1", SNMP_v2c: "SNMPv2c"}[sv],
                    status=False,
                    error=CheckError(code="0", message="Not getting OID on Profile Discovery"),
                )
