# ----------------------------------------------------------------------
# NOC Checker Base class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass(frozen=True)
class CheckResult(object):
    check: str
    status: bool
    skipped: bool = False
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class Check(object):
    name: str
    arg0: Optional[str] = None


class Checker(object):
    """ """

    name: str
    CHECKS: List[str]

    def __init__(self, c_object):
        self.object = c_object

    def run(self, checks: List[Check]) -> List[CheckResult]:
        """
        Do check and return result
        :param checks:
        :return:
        """
        ...
