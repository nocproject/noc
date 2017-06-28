# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.mrtconfig application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.sa.models.mrtconfig import MRTConfig
from noc.core.translation import ugettext as _


class MRTConfigApplication(ExtDocApplication):
    """
    MRTConfig application
    """
    title = _("MRT Config")
    menu = [_("Setup"), _("MRT Config")]
    model = MRTConfig
