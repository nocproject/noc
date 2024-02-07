# ----------------------------------------------------------------------
# IPPrefixProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class IPPrefixProfile(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    workflow: Optional[str] = None
