# ----------------------------------------------------------------------
# NOC Checker Base class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union, Iterable, Literal

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
    field: Literal["user", "password", "super_password", "profile", "snmp_ro", "snmp_rw", "schema"]
    op: Literal["set", "reset"] = "set"
    value: Optional[str] = None


@dataclass(frozen=True)
class CheckResult(object):
    check: str
    status: bool  # True - OK, False - Fail
    arg0: Optional[str] = None  # Checked Argument
    skipped: bool = False  # Check was skipped (Example, no credential)
    error: Optional[str] = None  # Description if Fail
    data: Optional[Dict[str, Any]] = None  # Collected check data
    # Action: Set Profile, Credential, Send Notification (Diagnostic Header) ?
    # action: Optional[Union[ProfileSet, CLICredentialSet, SNMPCredentialSet]] = None
    credentials: Optional[List[CredentialItem]] = None
    caps: Optional[List[CapsItem]] = None
    # Metrics collected
    metrics: Optional[List[MetricValue]] = None


@dataclass(frozen=True)
class CheckData(object):
    name: str
    status: bool  # True - OK, False - Fail
    skipped: bool = False  # Check was skipped (Example, no credential)
    arg0: Optional[str] = None
    error: Optional[str] = None  # Description if Fail
    data: Optional[Dict[str, Any]] = None  # Collected check data


@dataclass(frozen=True)
class Check(object):
    name: str
    arg0: Optional[str] = None

    def __str__(self):
        return f"{self.name}:{self.arg0 or ''}"


class Checker(object):
    """
    Base class for Checkers. Check some facts and return result
    """

    name: str
    CHECKS: List[str]
    USER_DISCOVERY_USE: bool = True  # Allow use in User Discovery

    def iter_result(
        self, checks: Optional[List[Union[Check, str]]] = None
    ) -> Iterable[CheckResult]:
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
