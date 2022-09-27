# ----------------------------------------------------------------------
# SNMP checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable, Dict

# NOC modules
from .base import Check, ObjectChecker, CheckResult, CredentialSet
from ..script.credentialchecker import CredentialChecker as CredentialCheckerScript
from ..script.scheme import Protocol


class SNMPProtocolChecker(ObjectChecker):
    """
    Check ManagedObject supported access protocols and credential
    """

    name = "snmpprotocolchecker"
    CHECKS: List[str] = ["SNMPv1", "SNMPv2c"]
    PROTO_CHECK_MAP: Dict[str, Protocol] = {p.config.check: p for p in Protocol if p.config.check}

    def iter_result(self, checks=None) -> Iterable[CheckResult]:
        cc = CredentialCheckerScript(
            self.object.address,
            self.object.pool,
            self.object.effective_labels,
            logger=self.logger,
            calling_service=self.calling_service,
        )
        protocols: List[Protocol] = []
        for c in checks or []:
            if isinstance(c, Check):
                c = c.name
            if c not in self.PROTO_CHECK_MAP:
                continue
            protocols += [self.PROTO_CHECK_MAP[c]]
        action = None
        for proto_r in cc.iter_result(protocols):
            if not protocols:
                break
            if proto_r.status and proto_r.credential:
                action = CredentialSet(
                    snmp_ro=proto_r.credential.snmp_ro, snmp_rw=proto_r.credential.snmp_rw
                )
            if action:
                protocols.pop(proto_r.protocol, None)
            yield CheckResult(
                check=proto_r.protocol.config.check,
                status=proto_r.status,
                error=proto_r.error,
                skipped=proto_r.skipped,
                action=action,
            )
