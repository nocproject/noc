# ----------------------------------------------------------------------
# NOC Checker Base class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Iterable, Literal, Union
from noc.core.script.scheme import SNMPCredential, SNMPv3Credential, CLICredential, HTTPCredential

# NOC modules
from noc.core.log import PrefixLoggerAdapter


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
    field: Literal["user", "password", "super_password", "profile", "snmp_ro", "snmp_rw", "scheme"]
    op: Literal["set", "reset"] = "set"
    value: Optional[str] = None


@dataclass(frozen=True)
class Check(object):
    name: str  # Check name
    address: str  # IP Address
    port: Optional[int] = None  # TCP/UDP port
    arg0: Optional[str] = None  #
    pool: Optional[str] = None  # Address Pool
    suggests_credential: bool = False
    credentials: Optional[List[Union[SNMPCredential, SNMPv3Credential, CLICredential, HTTPCredential]]] = None  # Credentials List

    @classmethod
    def from_string(cls, url) -> "Check":
        """

        :param url:
        :return:
        """


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
    credentials: Optional[List[Union[SNMPCredential, SNMPv3Credential, CLICredential, HTTPCredential]]] = None
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

    def __init__(self, logger=None, calling_service: Optional[str] = None):
        self.logger = PrefixLoggerAdapter(
            logger or logging.getLogger(self.name),
            f"{calling_service or self.name}]",
        )
        self.calling_service = calling_service or self.name

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

    def __init__(self, c_object, logger=None, calling_service: Optional[str] = None):
        self.object = c_object
        self.logger = PrefixLoggerAdapter(
            logger or logging.getLogger(self.name),
            f"{self.object.pool or ''}][{self.object or ''}",
        )
        self.calling_service = calling_service or self.name
