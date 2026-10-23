# ----------------------------------------------------------------------
# IPPrefixProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel


class IPPrefixProfile(BaseModel):
    id: str
    name: str
    description: str | None = None
    workflow: str | None = None
