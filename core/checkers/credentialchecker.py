# ----------------------------------------------------------------------
# Credential checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import List

# NOC modules
from .base import Check, Checker, CheckResult
from ..script.credentialchecker import CredentialChecker as CredentialCheckerScript
from ..script.credentialchecker import Protocol


class CredentialChecker(Checker):
    base_logger = logging.getLogger("credentialchecker")
    name = "credentialchecker"
    CHECKS: List[str] = ["TELNET", "SSH", "SNMPv1", "SNMPv2c"]
    PROTO_CHECK_MAP = {p.check: p for p in Protocol if p.config.check}

    def run(self, checks: List[Check]) -> List[CheckResult]:
        """
        :param checks:
        :return:
        """
        cc = CredentialCheckerScript(
            self.object.address,
            self.object.pool,
            self.object.labels,
            profile=self.object.profile.name,
        )
        r = cc.do_check(*[self.PROTO_CHECK_MAP[c.name] for c in checks])
        # @todo set credential

        return [CheckResult(check=pr.protocol.config.check, status=pr.status, error=pr.error) for pr in r]
