# ----------------------------------------------------------------------
# IP Address ProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel


class IPAddressProfile(BaseModel):
    id: str
    name: str
    description: str | None = None
    workflow: str | None = None
