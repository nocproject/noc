# ----------------------------------------------------------------------
# NetworkSegmentModel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

from .base import BaseModel
from .networksegmentprofile import NetworkSegmentProfile
from .typing import Reference


class NetworkSegment(BaseModel):
    id: str
    name: str
    parent: Reference["NetworkSegment"] | None = None
    sibling: Reference["NetworkSegment"] | None = None
    profile: Reference["NetworkSegmentProfile"] = None

    _csv_fields = ["id", "parent", "name", "sibling", "profile"]
