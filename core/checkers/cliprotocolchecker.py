# ----------------------------------------------------------------------
# CLI checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Iterable, Dict

# NOC modules
from .base import Check, ObjectChecker, CheckResult, CredentialItem
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
            labels=self.object.effective_labels,
            port=self.object.port or None,
            credentials=credential,
            profile=self.object.profile,
            logger=self.logger,
            calling_service=self.calling_service,
            raise_privilege=self.object.to_raise_privileges,
            ignoring_rule=self.object.auth_profile
            and not self.object.auth_profile.enable_suggest_by_rule,
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
        credentials = None
        r = {}
        for proto_r in cc.iter_result(protocols):
            if proto_r.protocol not in protocols:
                continue
            r[proto_r.protocol] = proto_r
            if not credentials and proto_r.status and proto_r.credential:
                credentials = [
                    CredentialItem(field="user", value=proto_r.credential.user),
                    CredentialItem(field="password", value=proto_r.credential.password),
                    CredentialItem(field="super_password", value=proto_r.credential.super_password),
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
