# ----------------------------------------------------------------------
# ManagedObjectProfileModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class ManagedObjectProfile(BaseModel):
    id: str
    name: str
    level: Optional[int] = 25

    _csv_fields = ["id", "name", "level"]
