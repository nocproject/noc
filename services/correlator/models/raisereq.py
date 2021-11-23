# ---------------------------------------------------------------------
# Raise Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any, List

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # py3.7 support


# Third-party modules
from pydantic import BaseModel, Field


class GroupItem(BaseModel):
    reference: str
    alarm_class: Optional[str]
    name: Optional[str]


class RaiseRequest(BaseModel):
    op: Literal["raise"] = Field(None, alias="$op")
    reference: str
    managed_object: str
    alarm_class: str
    timestamp: Optional[str]
    groups: Optional[List[GroupItem]]
    vars: Optional[Dict[str, Any]]
    labels: Optional[List[str]]
    remote_system: Optional[str]
    remote_id: Optional[str]
