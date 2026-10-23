# ----------------------------------------------------------------------
# NetworkSegmentModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from .base import BaseModel
from .typing import Reference
from .networksegmentprofile import NetworkSegmentProfile


class NetworkSegment(BaseModel):
    id: str
    name: str
    parent: Reference["NetworkSegment"] | None = None
    sibling: Reference["NetworkSegment"] | None = None
    profile: Reference["NetworkSegmentProfile"] = None

    _csv_fields = ["id", "parent", "name", "sibling", "profile"]
