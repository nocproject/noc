# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.action application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.sa.models.action import Action
from noc.core.translation import ugettext as _


class ActionApplication(ExtDocApplication):
    """
    Action application
    """
    title = _("Action")
    menu = [_("Setup"), _("Actions")]
    model = Action
