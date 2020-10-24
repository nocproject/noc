# ----------------------------------------------------------------------
# Network Segment Profile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.networksegmentprofile import NetworkSegmentProfileModel
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile


class NetworkSegmentProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """

    name = "networksegmentprofile"
    model = NetworkSegmentProfile
    data_model = NetworkSegmentProfileModel
    fields = ["id", "name"]
