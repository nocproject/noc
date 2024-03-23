# ----------------------------------------------------------------------
# NOC Checker Base class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Iterable, Literal, Union

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.script.scheme import SNMPCredential, SNMPv3Credential, CLICredential, HTTPCredential
from noc.core.script.caller import ScriptCaller


@dataclass(frozen=True)
class MetricValue(object):
    metric_type: str
    value: float
    labels: Optional[List[str]] = None


@dataclass(frozen=True)
class CapsItem(object):
    caps: str
    value: Optional[str] = None
    scope: Optional[str] = None
    # source diagnostic
    # scope - diagnostic_name


@dataclass(frozen=True)
class CredentialItem(object):
    field: Literal["user", "password", "super_password", "+", "snmp_ro", "snmp_rw", "scheme"]
    op: Literal["set", "reset"] = "set"
    value: Optional[str] = None


@dataclass(frozen=True, eq=True)
class Check(object):
    name: str  # Check name
    port: Optional[int] = None  # TCP/UDP port
    arg0: Optional[str] = None  #
    # pool: Optional[str] = field(default=None, hash=False)  # Address Pool
    address: str = field(default=None, compare=False)  # IP Address
    credentials: Optional[
        List[Union[SNMPCredential, SNMPv3Credential, CLICredential, HTTPCredential]]
    ] = field(default=None, compare=False)

    def __hash__(self):
        if self.address or self.port:
            return hash((self.name, self.address or "", self.port or 0, self.arg0 or ""))
        return hash((self.name, self.arg0 or ""))

    def arg(self) -> str:
        r = []
        if self.address:
            r.append(f"address={self.address}")
        if self.port:
            r.append(f"port={self.port}")
        if self.arg0:
            r.append(f"arg0={self.arg0}")
        return "&".join(r)

    @classmethod
    def from_string(cls, url) -> "Check":
        """
        <check>://<cred>@<address>:<port>&arg0
        :param url:
        :return:
        """

    @property
    def snmp_credential(self) -> Optional[SNMPCredential]:
        for c in self.credentials:
            if isinstance(c, SNMPCredential):
                return c


@dataclass(frozen=True)
class CheckResult(object):
    check: str
    status: bool  # True - OK, False - Fail
    arg0: Optional[str] = None  # Checked Argument
    skipped: bool = False  # Check was skipped (Example, no credential)
    is_available: Optional[bool] = None  # Port/Address is available
    port: Optional[int] = None
    is_access: Optional[bool] = None  # Access to resource for credential
    error: Optional[str] = None  # Description if Fail
    data: Optional[Dict[str, Any]] = None  # Collected check data
    # Action: Set Profile, Credential, Send Notification (Diagnostic Header) ?
    # action: Optional[Union[ProfileSet, CLICredentialSet, SNMPCredentialSet]] = None
    # Credentials List, Return if suggests flag is set
    credentials: Optional[
        List[Union[SNMPCredential, SNMPv3Credential, CLICredential, HTTPCredential]]
    ] = None
    caps: Optional[List[CapsItem]] = None
    # Metrics collected
    metrics: Optional[List[MetricValue]] = None


class Checker(object):
    """
    Base class for Checkers. Check some facts and return result
    """

    name: str
    CHECKS: List[str]
    USER_DISCOVERY_USE: bool = True  # Allow use in User Discovery

    def __init__(
        self,
        *,
        logger=None,
        calling_service: Optional[str] = None,
        pool: Optional[str] = None,
        **kwargs,
    ):
        self.logger = PrefixLoggerAdapter(
            logger or logging.getLogger(self.name),
            f"{calling_service or self.name}]",
        )
        self.calling_service = calling_service or self.name
        # Set for pooled check
        self.pool = pool
        self.object = kwargs.get("object")
        self._script_caller: Optional["ScriptCaller"] = None

    def get_script(self, name: str) -> "ScriptCaller":
        if not self._script_caller and not self.object:
            raise NotImplementedError()
        if not self._script_caller:
            o = lambda: None  # noqa:E731
            o.id = self.object
            self._script_caller = ScriptCaller(o, name)
        return self._script_caller

    def iter_result(self, checks: List[Check]) -> Iterable[CheckResult]:
        """
        Iterate over result
        :param checks: List checks param for run
        :return:
        """
        ...


class ObjectChecker(Checker):
    """
    Checkers supported ManagedObject
    """

    def __init__(self, o, **kwargs):
        self.object = o
        super().__init__(**kwargs)
        # super().__init__(
        #     logger=PrefixLoggerAdapter(
        #         logger or logging.getLogger(self.name),
        #         f"{self.pool or ''}][{self.o_name or ''}",
        #     ),
        # )
