# ----------------------------------------------------------------------
# Script credential diagnostic
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import List, Iterable, Optional, Tuple

# NOC modules
from noc.core.script.scheme import Protocol, SNMPCredential, SNMPv3Credential, CLICredential
from noc.core.checkers.base import Check, CheckResult, DataItem
from noc.core.diagnostic.types import DiagnosticConfig, CheckStatus, DiagnosticState
from noc.core.profile.loader import GENERIC_PROFILE
from noc.core.models.inputsources import InputSource
from noc.sa.models.credentialcheckrule import CredentialCheckRule


class SNMPSuggestsDiagnostic:
    """
    Run diagnostic by config and check status
    """

    def __init__(self, config: DiagnosticConfig, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger("snmpsuggestsdiagnostic")

    def iter_checks(
        self,
        address: str,
        labels: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        suggests_snmp: bool = True,
        **kwargs,
    ) -> Iterable[Tuple[Check, ...]]:
        r = []
        labels = set(labels or [])
        if self.config.checks:
            r += self.config.checks
        if not suggests_snmp:
            yield tuple(x for x in r if x.credential)
            return
        for s in CredentialCheckRule.get_suggest_rules():
            if not s.is_match(labels):
                continue
            for c in s.credentials:
                if isinstance(c, SNMPCredential):
                    r += [
                        Check(name=Protocol.SNMPv1.config.check, address=address, credential=c),
                        Check(name=Protocol.SNMPv2c.config.check, address=address, credential=c),
                    ]
                elif isinstance(c, SNMPv3Credential):
                    r.append(
                        Check(name=Protocol.SNMPv3.config.check, address=address, credential=c)
                    )
        yield tuple(r)

    def get_check_status(
        self,
        checks: List[CheckStatus],
        **kwargs,
    ) -> Tuple[Optional[DiagnosticState], Optional[str]]:
        """Getting Diagnostic result: State and reason"""
        error = ""
        for c in checks:
            if c.skipped:
                continue
            if c.error:
                error = c.error
            if c.status:
                return DiagnosticState.enabled, None
        return DiagnosticState.failed, error

    def process_result(
        self,
        checks: List[CheckResult],
        source: Optional[InputSource] = InputSource.UNKNOWN,
    ) -> Tuple[List[CheckStatus], List[DataItem]]:
        """Processed checks result and Return Status"""
        return [CheckStatus.from_result(c, source=source) for c in checks], []


class CLISuggestsDiagnostic:
    """
    Run diagnostic by config and check status
    """

    def __init__(self, config: DiagnosticConfig, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger("clisuggestsdiagnostic")

    def iter_checks(
        self,
        address: str,
        labels: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        profile: Optional[str] = None,
        suggests_cli: bool = True,
        **kwargs,
    ) -> Iterable[Tuple[Check, ...]]:
        r = []
        labels = set(labels or [])
        if not profile or profile == GENERIC_PROFILE:
            self.logger.info("Generic profile not checked for CLI")
            return
        raise_privilege, port = False, None
        for c in self.config.checks or []:
            if c.credential:
                raise_privilege |= c.credential.raise_privilege
            port = c.port
            r.append(
                Check(
                    name=c.name,
                    address=c.address,
                    port=c.port,
                    args={"arg0": profile},
                    credential=c.credential,
                )
            )
        if not suggests_cli:
            yield r
        for s in CredentialCheckRule.get_suggest_rules():
            if not s.is_match(labels):
                continue
            for cr in s.credentials:
                if not isinstance(cr, CLICredential):
                    continue
                for p in cr.enable_protocols:
                    p = Protocol(p)
                    r.append(
                        Check(
                            name=p.config.check,
                            address=address,
                            port=port,
                            args={"arg0": profile},
                            credential=CLICredential(
                                username=cr.username,
                                password=cr.password,
                                super_password=cr.super_password,
                                raise_privilege=raise_privilege,
                                enable_protocols=(p,),
                            ),
                        )
                    )
        yield r

    def get_check_status(
        self,
        checks: List[CheckStatus],
        **kwargs,
    ) -> Tuple[Optional[DiagnosticState], Optional[str]]:
        """Getting Diagnostic result: State and reason"""
        error = ""
        status = DiagnosticState.failed
        for c in checks:
            if c.skipped:
                continue
            if c.error:
                error = c.error
            if c.status and not status:
                status = DiagnosticState.enabled
                # return True, None, {}, []
        if status:
            return DiagnosticState.enabled, None
        return DiagnosticState.failed, error

    def process_result(
        self,
        checks: List[CheckResult],
        source: Optional[InputSource] = InputSource.UNKNOWN,
    ) -> Tuple[List[CheckStatus], List[DataItem]]:
        """Processed checks result and Return Status"""
        return [CheckStatus.from_result(c, source=source) for c in checks], []
