# ----------------------------------------------------------------------
# NetworkSegmentModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from .base import BaseModel


class NetworkSegmentModel(BaseModel):
    id: str
    parent: Optional[str]
    name: str
    sibling: Optional[str]
    profile: str

    _csv_fields = ["id", "parent", "name", "sibling", "profile"]
