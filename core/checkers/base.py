# ----------------------------------------------------------------------
# NOC Checker Base class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from functools import partial
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, AsyncIterable

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.script.scheme import SNMPCredential, SNMPv3Credential, CLICredential, HTTPCredential


TCP_CHECK = "TCP"
CHECKS = []


@dataclass(frozen=True)
class MetricValue(object):
    metric_type: str
    value: float
    labels: Optional[List[str]] = None


@dataclass(frozen=True)
class DataItem(object):
    name: str
    value: Any
    scope: Optional[str] = None  # caps/attribute


@dataclass(frozen=True, eq=True)
class Check(object):
    name: str  # Check name
    args: Optional[Dict[str, str]] = None  #
    # pool: Optional[str] = field(default=None, hash=False)  # Address Pool
    address: str = field(default=None, compare=False)  # IP Address
    port: Optional[int] = None  # TCP/UDP port
    script: Optional[str] = None
    credential: Optional[
        Union[
            SNMPCredential,
            SNMPv3Credential,
            CLICredential,
            HTTPCredential,
        ]
    ] = field(default=None, compare=False, hash=False)

    def __str__(self):
        return f"{self.name}?{self.args}"

    def __hash__(self):
        return hash(self.key)

    @property
    def key(self) -> str:
        """Check key"""
        return f"{self.name},{self.arg}"

    @property
    def arg0(self):
        if self.args:
            return self.args.get("arg0")
        return

    @property
    def arg(self) -> str:
        r = []
        if self.script:
            r.append(f"script={self.script}")
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

    @classmethod
    def from_dict(cls, data) -> "Check":
        credential = data.pop("credential", None)
        if credential and "snmp_ro" in credential:
            credential = SNMPCredential(**credential)
        elif credential and "context" in credential:
            credential = SNMPv3Credential(**credential)
        elif credential and "super_password" in credential:
            credential = CLICredential(**credential)
        if credential:
            data["credential"] = credential
        return Check(**data)

    @property
    def snmp_credential(self) -> Optional[SNMPCredential]:
        if isinstance(self.credential, SNMPCredential):
            return self.credential
        return None

    def set_credential(self, cred) -> "Check":
        return Check(
            name=self.name,
            args=self.args,
            address=self.address,
            port=self.port,
            script=self.script,
            credential=cred,
        )


@dataclass(frozen=True)
class CheckError(object):
    code: str  # Error code
    message: Optional[str] = None  # Description if Fail
    is_access: Optional[bool] = None  # Access to resource for credential
    is_available: Optional[bool] = None  # Port/Address is available


@dataclass(frozen=True)
class CheckResult(object):
    check: str
    status: bool  # True - OK, False - Fail
    args: Optional[Dict[str, Any]] = None  # Checked Argument
    port: Optional[int] = None
    address: Optional[str] = None
    script: Optional[str] = None
    skipped: bool = False  # Check was skipped (Example, no credential)
    error: Optional[CheckError] = None  # Set if fail
    data: Optional[List[DataItem]] = None  # Collected check data
    # Action: Set Profile, Credential, Send Notification (Diagnostic Header) ?
    # caps: Optional[List[CapsItem]] = None
    # Metrics collected
    metrics: Optional[List[MetricValue]] = None
    # Credentials List, Return if suggests flag is set
    credential: Optional[Union[SNMPCredential, SNMPv3Credential, CLICredential, HTTPCredential]] = (
        None
    )

    def __str__(self):
        return f"{self.check}?{self.args}: {self.status}"

    def __hash__(self):
        return hash(self.key)

    @property
    def key(self) -> str:
        """Check key"""
        return f"{self.check},{self.arg}"

    @property
    def arg(self) -> str:
        r = []
        if self.script:
            r.append(f"script={self.script}")
        if self.address:
            r.append(f"address={self.address}")
        if self.port:
            r.append(f"port={self.port}")
        if self.arg0:
            r.append(f"arg0={self.arg0}")
        return "&".join(r)

    @property
    def arg0(self):
        if self.args:
            return self.args.get("arg0")
        return

    @classmethod
    def from_dict(cls, v) -> "CheckResult":
        data = []
        for d in v.pop("data") or []:
            data.append(DataItem(**d))
        if v["error"]:
            v["error"] = CheckError(**v["error"])
        v["data"] = data
        cred = v.pop("credential", None)
        if not cred:
            return CheckResult(**v)
        if "snmp_ro" in cred:
            cred = SNMPCredential(**cred)
        elif "username" in cred and "password" not in cred:
            cred = SNMPv3Credential(**cred)
        else:
            cred = CLICredential(**cred)
        v["credential"] = cred
        return CheckResult(**v)


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
        **kwargs,
    ):
        self.logger = PrefixLoggerAdapter(logger or logging.getLogger(self.name), self.name)
        self.address = kwargs.get("address")

    def iter_result(self, checks: List[Check]) -> AsyncIterable[CheckResult]:
        """
        Iterate over result checks
        Args:
            checks: List checks param for run
        """
        raise NotImplementedError()
