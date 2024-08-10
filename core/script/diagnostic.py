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
from noc.core.checkers.base import Check, CheckResult
from noc.core.wf.diagnostic import DiagnosticConfig
from noc.sa.models.credentialcheckrule import CredentialCheckRule
from noc.sa.models.profile import GENERIC_PROFILE


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
                        Check(
                            name=Protocol.SNMPv1.config.check, address=self.address, credential=c
                        ),
                        Check(
                            name=Protocol.SNMPv2c.config.check, address=self.address, credential=c
                        ),
                    ]
                elif isinstance(c, SNMPv3Credential):
                    r.append(
                        Check(name=Protocol.SNMPv3.config.check, address=self.address, credential=c)
                    )
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
        cred: Optional[Union[SNMPCredential, SNMPv3Credential]] = None,
        **kwargs,
    ):
        self.config = cfg
        self.labels = set(labels or [])
        self.logger = logger or logging.getLogger("clisuggestsdiagnostic")
        self.address = address
        self.profile = profile
        self.cred = cred

    def iter_checks(self) -> Iterable[Tuple[Check, ...]]:
        r = []
        if not self.profile or self.profile == GENERIC_PROFILE:
            self.logger.info("Generic profile not checked for CLI")
            return
        for c in self.config.checks:
            r.append(
                Check(
                    name=c.name,
                    address=c.address,
                    port=c.port,
                    args={"arg0": self.profile},
                    credential=c.credential,
                )
            )
            for s in CredentialCheckRule.get_suggest_rules():
                if not s.is_match(self.labels):
                    continue
                for cr in s.credentials:
                    if isinstance(cr, CLICredential):
                        r.append(
                            Check(
                                name=c.name,
                                address=c.address,
                                port=c.port,
                                args={"arg0": self.profile},
                                credential=cr,
                            )
                        )
        yield r

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
