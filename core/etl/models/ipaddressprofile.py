# ----------------------------------------------------------------------
# IP Address ProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class IPAddressProfile(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    workflow: Optional[str] = None
