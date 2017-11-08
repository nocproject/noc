# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.networksegmentprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile
# NOC modules
from noc.lib.app import ExtDocApplication


class NetworkSegmentProfileApplication(ExtDocApplication):
    """
    NetworkSegmentProfile application
    """
    title = "Network Segment Profile"
    menu = [_("Setup"), _("Network Segment Profiles")]
    model = NetworkSegmentProfile
