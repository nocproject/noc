# ----------------------------------------------------------------------
# Job Problem DataClass
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass, field

# Third-party modules
from typing import List, Dict, Optional, Any


@dataclass(frozen=True)
class ProblemItem(object):
    alarm_class: Optional[str]
    message: str = ""
    path: List[str] = field(default_factory=list)
    fatal: bool = False
    vars: Dict[str, Any] = field(default_factory=dict)
    code: Optional[str] = None
    check: Optional[str] = None
