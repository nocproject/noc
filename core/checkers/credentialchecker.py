# ----------------------------------------------------------------------
# Credential checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Optional

# NOC modules
from .base import Check, ObjectChecker, CheckResult, CredentialSet
from ..script.credentialchecker import CredentialChecker as CredentialCheckerScript
from ..script.credentialchecker import Protocol, SNMPCredential, CLICredential


class CredentialChecker(ObjectChecker):
    """
    Check ManagedObject supported access protocols and credential
    """

    name = "credentialchecker"
    CHECKS: List[str] = ["TELNET", "SSH", "SNMPv1", "SNMPv2c"]
    PROTO_CHECK_MAP = {p.config.check: p for p in Protocol if p.config.check}

    def run(self, checks: List[Check], calling_service: Optional[str] = None) -> List[CheckResult]:
        """
        :param checks:
        :param calling_service:
        :return:
        """
        cc = CredentialCheckerScript(
            self.object.address,
            self.object.pool,
            self.object.effective_labels,
            profile=self.object.profile,
            calling_service=calling_service or self.name,
        )
        r = []
        # @todo Bad interface, need reworked
        for sr in cc.do_check(*[self.PROTO_CHECK_MAP[c.name] for c in checks]):
            action = None
            if not action and sr.credential:
                if isinstance(sr.credential, SNMPCredential):
                    action = CredentialSet(snmp_ro=sr.credential.snmp_ro)
                elif isinstance(sr.credential, CLICredential):
                    action = CredentialSet(
                        user=sr.credential.user,
                        password=sr.credential.password,
                        super_password=sr.credential.super_password,
                    )
            for pr in sr.protocols:
                r += [
                    CheckResult(
                        check=pr.protocol.config.check,
                        status=pr.status,
                        error=pr.error,
                        skipped=pr.skipped,
                        action=action,
                    )
                ]
        return r
