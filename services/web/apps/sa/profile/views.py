# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# sa.profile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.sa.models.profile import Profile
from noc.core.translation import ugettext as _


class ProfileApplication(ExtDocApplication):
    """
    Profile application
    """
    title = "Profile"
    menu = [_("Setup"), _("Profiles")]
    model = Profile
