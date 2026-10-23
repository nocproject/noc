# ----------------------------------------------------------------------
# Network Segment Profile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.networksegmentprofile import NetworkSegmentProfile
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile as NetworkSegmentProfileModel


class NetworkSegmentProfileLoader(BaseLoader):
    """
    Managed Object Profile loader
    """

    name = "networksegmentprofile"
    model = NetworkSegmentProfileModel
    data_model = NetworkSegmentProfile
    fields = ["id", "name"]
