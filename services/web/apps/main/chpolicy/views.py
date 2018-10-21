# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.chpolicy application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.chpolicy import CHPolicy
from noc.core.translation import ugettext as _


class CHPolicyApplication(ExtDocApplication):
    """
    CHPolicy application
    """
    title = "CHPolicy"
    menu = [_("Setup"), _("CH Policies")]
    model = CHPolicy
