# ----------------------------------------------------------------------
# inv.networksegmentprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile
from noc.services.web.base.extdocapplication import ExtDocApplication


class NetworkSegmentProfileApplication(ExtDocApplication):
    """
    NetworkSegmentProfile application
    """

    title = "Network Segment Profile"
    menu = [_("Setup"), _("Network Segment Profiles")]
    model = NetworkSegmentProfile
