# ----------------------------------------------------------------------
# SNMP checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable, Dict

# NOC modules
from .base import Check, ObjectChecker, CheckResult, CredentialItem
from ..script.credentialchecker import CredentialChecker as CredentialCheckerScript, SNMPCredential
from ..script.scheme import Protocol


class SNMPProtocolChecker(ObjectChecker):
    """
    Check ManagedObject supported access protocols and credential
    """

    name = "snmpprotocolchecker"
    CHECKS: List[str] = ["SNMPv1", "SNMPv2c"]
    PROTO_CHECK_MAP: Dict[str, Protocol] = {p.config.check: p for p in Protocol if p.config.check}

    def iter_result(self, checks=None) -> Iterable[CheckResult]:
        credential = None
        if self.object.credentials.snmp_ro or self.object.credentials.snmp_rw:
            credential = [
                SNMPCredential(
                    snmp_ro=self.object.credentials.snmp_ro,
                    snmp_rw=self.object.credentials.snmp_rw,
                )
            ]
        cc = CredentialCheckerScript(
            self.object.address,
            self.object.pool,
            self.object.effective_labels,
            credentials=credential,
            logger=self.logger,
            calling_service=self.calling_service,
            ignoring_rule=self.object.auth_profile
            and not self.object.auth_profile.enable_suggest_by_rule,
        )
        protocols: List[Protocol] = []
        for c in checks or []:
            if isinstance(c, Check):
                c = c.name
            if c not in self.PROTO_CHECK_MAP:
                continue
            protocols += [self.PROTO_CHECK_MAP[c]]
        credentials = None
        r = {}
        for proto_r in cc.iter_result(protocols):
            if proto_r.protocol not in protocols:
                continue
            r[proto_r.protocol] = proto_r
            if not credentials and proto_r.status and proto_r.credential:
                credentials = [
                    CredentialItem(field="snmp_ro", value=proto_r.credential.snmp_ro),
                    CredentialItem(field="snmp_rw", value=proto_r.credential.snmp_rw),
                    CredentialItem(field="auth_profile", op="reset"),
                ]
            if credentials and len(protocols) == len(r):
                break
        for x in r.values():
            yield CheckResult(
                check=x.protocol.config.check,
                status=x.status,
                error=x.error,
                skipped=x.skipped,
                credentials=credentials,
            )
