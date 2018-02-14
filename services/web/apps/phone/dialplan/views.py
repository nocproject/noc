# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# phone.dialplan application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.phone.models.dialplan import DialPlan
from noc.core.translation import ugettext as _


class DialPlanApplication(ExtDocApplication):
    """
    DialPlan application
    """
    title = "DialPlan"
    menu = [_("Setup"), _("DialPlan")]
    model = DialPlan
