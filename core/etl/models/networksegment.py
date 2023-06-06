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
    name: str
    parent: Optional[Reference["NetworkSegment"]] = None
    sibling: Optional[Reference["NetworkSegment"]] = None
    profile: Reference["NetworkSegmentProfile"] = None

    _csv_fields = ["id", "parent", "name", "sibling", "profile"]
