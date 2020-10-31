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
from .typing import Reference
from .networksegmentprofile import NetworkSegmentProfile


class NetworkSegment(BaseModel):
    id: str
    parent: Optional[Reference["NetworkSegment"]]
    name: str
    sibling: Optional[Reference["NetworkSegment"]]
    profile: Reference["NetworkSegmentProfile"]

    _csv_fields = ["id", "parent", "name", "sibling", "profile"]
