# ----------------------------------------------------------------------
# CLI checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable, Dict

# NOC modules
from .base import Check, ObjectChecker, CheckResult, CredentialSet
from ..script.credentialchecker import CredentialChecker as CredentialCheckerScript, CLICredential
from ..script.scheme import Protocol


class CLIProtocolChecker(ObjectChecker):
    """
    Check ManagedObject supported access protocols and credential
    """

    name = "cliprotocolchecker"
    CHECKS: List[str] = ["TELNET", "SSH"]
    PROTO_CHECK_MAP: Dict[str, Protocol] = {p.config.check: p for p in Protocol if p.config.check}

    def iter_result(self, checks=None) -> Iterable[CheckResult]:
        credential = None
        if self.object.scheme == "HTTP" or self.object.scheme == "HTTPS":
            return
        if self.object.credentials.user or self.object.credentials.password:
            credential = [
                CLICredential(
                    user=self.object.credentials.user,
                    password=self.object.credentials.password,
                    super_password=self.object.credentials.super_password,
                )
            ]
        cc = CredentialCheckerScript(
            self.object.address,
            self.object.pool,
            self.object.effective_labels,
            credentials=credential,
            profile=self.object.profile,
            logger=self.logger,
            calling_service=self.calling_service,
            raise_privilege=self.object.to_raise_privileges,
        )
        protocols: List[Protocol] = []
        for c in checks or []:
            if isinstance(c, Check):
                c = c.name
            if c not in self.PROTO_CHECK_MAP:
                continue
            if self.PROTO_CHECK_MAP[c].value != self.object.scheme:
                yield CheckResult(check=c, status=True, skipped=True)
                continue
            protocols += [self.PROTO_CHECK_MAP[c]]
        action = None
        r = {}
        for proto_r in cc.iter_result(protocols):
            if proto_r.protocol not in protocols:
                continue
            if action and len(protocols) == len(r):
                break
            r[proto_r.protocol] = proto_r
            if not action and proto_r.status and proto_r.credential:
                action = CredentialSet(
                    user=proto_r.credential.user,
                    password=proto_r.credential.password,
                    super_password=proto_r.credential.super_password,
                )
        for x in r.values():
            yield CheckResult(
                check=x.protocol.config.check,
                status=x.status,
                error=x.error,
                skipped=x.skipped,
                action=action,
            )
