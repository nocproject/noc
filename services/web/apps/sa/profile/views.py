# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# sa.profile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app import ExtDocApplication
from noc.sa.models.profile import Profile


class ProfileApplication(ExtDocApplication):
    """
    Profile application
    """
    title = "Profile"
    menu = [_("Setup"), _("Profiles")]
    model = Profile
    query_fields = [
        "name__icontains", "description__icontains"
    ]
    default_ordering = ["name"]
