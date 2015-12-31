# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Network Segment loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseLoader
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.networksegment import NetworkSegment


class NetworkSegmentLoader(BaseLoader):
    """
    Network Segment loader
    """
    name = "networksegment"
    model = NetworkSegment
    fields = [
        "id",
        "parent",
        "name"
    ]

    mapped_fields = {
        "parent": "networksegment"
    }
