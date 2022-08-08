# ----------------------------------------------------------------------
# Credential checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable

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

    def iter_result(self, checks=None) -> Iterable[CheckResult]:
        cc = CredentialCheckerScript(
            self.object.address,
            self.object.pool,
            self.object.effective_labels,
            profile=self.object.profile,
            calling_service=self.calling_service,
        )
        protocols = []
        for c in checks or []:
            if isinstance(c, Check):
                c = c.name
            if c not in self.PROTO_CHECK_MAP:
                continue
            protocols += [self.PROTO_CHECK_MAP[c]]
        for sr in cc.do_check(*protocols):
            action = None
            if sr.credential and isinstance(sr.credential, SNMPCredential):
                action = CredentialSet(snmp_ro=sr.credential.snmp_ro)
            elif sr.credential and isinstance(sr.credential, CLICredential):
                action = CredentialSet(
                    user=sr.credential.user,
                    password=sr.credential.password,
                    super_password=sr.credential.super_password,
                )
            for pr in sr.protocols:
                yield CheckResult(
                    check=pr.protocol.config.check,
                    status=pr.status,
                    error=pr.error,
                    skipped=pr.skipped,
                    action=action,
                )
