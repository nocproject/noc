# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Network Segment Profile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.inv.models.networksegmentprofile import NetworkSegmentProfile

# NOC modules
from base import BaseLoader


class NetworkSegmentProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """
    name = "networksegmentprofile"
    model = NetworkSegmentProfile
    fields = [
        "id",
        "name"
    ]
