# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.networksegmentprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile
from noc.core.translation import ugettext as _


class NetworkSegmentProfileApplication(ExtDocApplication):
    """
    NetworkSegmentProfile application
    """
    title = "NetworkSegmentProfile"
    menu = [_("Setup"), _("Network Segment Profile")]
    model = NetworkSegmentProfile
