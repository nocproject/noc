# ----------------------------------------------------------------------
# Credential checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import List

# Third-party modules
import cachetools

# NOC modules
from .base import Check, Checker, CheckResult
from ..script.credentialchecker import CredentialChecker as CredentialCheckerScript
from ..script.credentialchecker import Protocol


class CredentialChecker(Checker):
    base_logger = logging.getLogger("credentialchecker")
    CHECKS: List[str] = ["TELNET", "SSH", "SNMPv1", "SNMPv2c"]

    def run(self, checks: List[Check]) -> List[CheckResult]:
        """
        :param checks:
        :return:
        """
        cc = CredentialCheckerScript(
            self.object.address,
            self.object.pool,
            self.object.labels,
            profile=self.object.profile.name
        )
        cc.do_check([p for p in Protocol if p.config.check and p.config.check in checks])
        sr = cc.result[0]
        r = []
        for proto in sr.protocols:
            r += [CheckResult(check=proto.config.check, status=True, error=sr.error)]
        return r
