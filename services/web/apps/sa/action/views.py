# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# sa.action application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.sa.models.action import Action


class ActionApplication(ExtDocApplication):
    """
    Action application
    """
    title = _("Action")
    menu = [_("Setup"), _("Actions")]
    model = Action
