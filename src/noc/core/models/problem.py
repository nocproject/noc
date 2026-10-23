# ----------------------------------------------------------------------
# Job Problem DataClass
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass, field

# Third-party modules
from typing import Any


@dataclass(frozen=True)
class ProblemItem:
    alarm_class: str | None
    message: str = ""
    path: list[str] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    fatal: bool = False
    diagnostic: str | None = None
    vars: dict[str, Any] = field(default_factory=dict)
    code: str | None = None
    check: str | None = None
