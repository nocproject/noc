# ----------------------------------------------------------------------
# Script credential diagnostic
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import List, Iterable, Optional, Tuple, Union, Dict, Any

# NOC modules
from noc.core.script.scheme import Protocol, SNMPCredential, SNMPv3Credential, CLICredential
from noc.core.checkers.snmp import SNMPv1, SNMPv2c, SNMPv3
from noc.sa.models.credentialcheckrule import CredentialCheckRule
from noc.sa.models.profile import GENERIC_PROFILE
from noc.core.wf.diagnostic import DiagnosticConfig
from noc.core.checkers.base import Check, CheckResult
from noc.core.service.client import open_sync_rpc
from noc.core.service.error import RPCError
from noc.core.text import safe_shadow


class SNMPSuggestsDiagnostic:
    """
    Run diagnostic by config and check status
    """

    def __init__(
        self,
        cfg: DiagnosticConfig,
        labels: Optional[List[str]] = None,
        logger=None,
        address: Optional[str] = None,
        cred: Optional[Union[SNMPCredential, SNMPv3Credential]] = None,
        **kwargs,
    ):
        self.config = cfg
        self.labels = set(labels or [])
        self.logger = logger or logging.getLogger("snmpsuggestsdiagnostic")
        self.address = address
        self.cred = cred

    def iter_checks(self) -> Iterable[Tuple[Check, ...]]:
        r = []
        if self.config.checks:
            r += self.config.checks
        for s in CredentialCheckRule.get_suggest_rules():
            if not s.is_match(self.labels):
                continue
            for c in s.credentials:
                if isinstance(c, SNMPCredential):
                    r += [
                        Check(name=SNMPv1, address=self.address, credential=c),
                        Check(name=SNMPv2c, address=self.address, credential=c),
                    ]
                elif isinstance(c, SNMPv3Credential):
                    r.append(Check(name=SNMPv3, address=self.address, credential=c))
        yield tuple(r)

    def get_result(
        self, checks: List[CheckResult]
    ) -> Optional[Tuple[Optional[bool], Optional[str], Optional[Dict[str, Any]]]]:
        """Getting Diagnostic result: State and reason"""
        error = ""
        for c in checks:
            if c.skipped:
                continue
            elif c.error and c.error.message:
                error = c.error.message
            if c.status:
                return True, None, {}
        return False, error, None


class CLISuggestsDiagnostic:
    """
    Run diagnostic by config and check status
    """

    def __init__(
        self,
        cfg: DiagnosticConfig,
        labels: Optional[List[str]] = None,
        logger=None,
        address: Optional[str] = None,
        profile: Optional[str] = None,
        pool: Optional[str] = None,
        cred: Optional[Union[SNMPCredential, SNMPv3Credential]] = None,
    ):
        self.config = cfg
        self.labels = set(labels or [])
        self.logger = logger or logging.getLogger("clisuggestsdiagnostic")
        self.address = address
        self.cred = cred
        self.profile = profile
        self.pool = pool

    def iter_checks(self) -> Iterable[Tuple[Check, ...]]:
        yield []

    def get_result(
        self, checks: List[CheckResult]
    ) -> Optional[Tuple[Optional[bool], Optional[str], Optional[Dict[str, Any]]]]:
        """Getting Diagnostic result: State and reason"""
        if not self.profile or self.profile == GENERIC_PROFILE:
            return
        for c in self.config.checks:
            if not isinstance(c.credential, CLICredential):
                continue
            if c.name == "TELNET":
                proto = Protocol(1)
                port = 21
            else:
                proto = Protocol(2)
                port = 22
            r, error = self.check_login(
                self.address,
                port,
                c.credential.user,
                c.credential.password,
                c.credential.super_password,
                protocol=proto,
                raise_privilege=c.credential.raise_privilege,
            )
            if r:
                return True, None, None
        return False, error, None

    def check_login(
        self,
        address: str,
        port: int,
        user: str,
        password: str,
        super_password: str,
        protocol: Protocol,
        raise_privilege: bool = True,
    ) -> Tuple[bool, str]:
        """
        Check user, password for cli proto
        Args:
            address:
            port:
            user:
            password:
            super_password:
            protocol:
            raise_privilege:
        """
        self.logger.debug("Checking %s: %s/%s/%s", protocol, user, password, super_password)
        self.logger.info(
            "Checking %s: %s/%s/%s",
            protocol,
            safe_shadow(user),
            safe_shadow(password),
            safe_shadow(super_password),
        )
        try:
            r = open_sync_rpc(
                "activator",
                pool=self.pool,
                calling_service="clisuggestsdiagnostic",  # calling_service=self.calling_service
            ).script(
                f"{self.profile}.login",
                {
                    "cli_protocol": protocol.config.alias,
                    "cli_port": port,
                    "address": address,
                    "user": user,
                    "password": password,
                    "super_password": super_password,
                    "path": None,
                    "raise_privileges": raise_privilege,
                    "access_preference": "C",
                },
            )
            self.logger.info("Result: %s, %s", r, r["message"])
            return bool(r["result"]), r["message"]  # bool(False) == bool(None)
        except RPCError as e:
            self.logger.debug("RPC Error: %s", e)
            return False, ""
