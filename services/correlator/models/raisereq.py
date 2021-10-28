# ---------------------------------------------------------------------
# Raise Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional, Dict, Any

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # py3.7 support


# Third-party modules
from pydantic import BaseModel, Field


class RaiseRequest(BaseModel):
    op: Literal["raise"] = Field(None, alias="$op")
    reference: str
    managed_object: str
    alarm_class: str
    timestamp: Optional[str]
    vars: Optional[Dict[str, Any]]
    remote_system: Optional[str]
    remote_id: Optional[str]
