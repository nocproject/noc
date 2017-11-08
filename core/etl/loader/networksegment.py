# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Network Segment loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from noc.inv.models.networksegment import NetworkSegment

## NOC modules
from base import BaseLoader


class NetworkSegmentLoader(BaseLoader):
    """
    Network Segment loader
    """
    name = "networksegment"
    model = NetworkSegment
    fields = [
        "id",
        "parent",
        "name",
        "sibling",
        "profile"
    ]

    mapped_fields = {
        "parent": "networksegment",
        "sibling": "networksegment",
        "profile": "networksegmentprofile"
    }
