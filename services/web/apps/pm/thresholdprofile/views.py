# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# pm.thresholdprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.pm.models.thresholdprofile import ThresholdProfile
from noc.core.translation import ugettext as _


class ThresholdProfileApplication(ExtDocApplication):
    """
    ThresholdProfile application
    """
    title = "ThresholdProfile"
    menu = [_("Setup"), _("Threshold Profiles")]
    model = ThresholdProfile
