# ----------------------------------------------------------------------
# NOC Checker Base class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union, Iterable

# NOC modules
from noc.core.log import PrefixLoggerAdapter


@dataclass(frozen=True)
class ProfileSet(object):
    profile: str
    action: str = "set_sa_profile"


@dataclass(frozen=True)
class MetricValue(object):
    metric_type: str
    value: float


@dataclass(frozen=True)
class CredentialSet(object):
    user: Optional[str] = None
    password: Optional[str] = None
    super_password: Optional[str] = None
    snmp_ro: Optional[str] = None
    snmp_rw: Optional[str] = None
    action: str = "set_credential"


@dataclass(frozen=True)
class CheckResult(object):
    check: str
    status: bool  # True - OK, False - Fail
    skipped: bool = False  # Check was skipped (Example, no credential)
    error: Optional[str] = None  # Description if Fail
    data: Optional[Dict[str, Any]] = None  # Collected check data
    # Action: Set Profile, Credential, Send Notification (Diagnostic Header) ?
    action: Optional[Union[ProfileSet, CredentialSet]] = None
    # Metrics collected
    metrics: Optional[List[MetricValue]] = None


@dataclass(frozen=True)
class CheckData(object):
    name: str
    status: bool  # True - OK, False - Fail
    skipped: bool = False  # Check was skipped (Example, no credential)
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

    def run(self, checks: List[Check]) -> List[CheckResult]:
        """
        Do check and return result
        :param checks:
        :param calling_service:
        :return:
        """
        ...

    def iter_result(self, checks: List[Check]) -> Iterable[CheckResult]:
        """

        :param checks:
        :return:
        """
        ...


class ObjectChecker(Checker):
    def __init__(self, c_object, logger=None, calling_service: Optional[str] = None):
        self.object = c_object
        self.logger = PrefixLoggerAdapter(
            logger or logging.getLogger(self.name),
            f"{self.object.pool or ''}][{self.object or ''}",
        )
        self.calling_service = calling_service or self.name
