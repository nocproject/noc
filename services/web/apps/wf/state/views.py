# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# wf.state application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.wf.models.state import State
from noc.core.translation import ugettext as _


class StateApplication(ExtDocApplication):
    """
    State application
    """
    title = _("States")
    menu = [_("Setup"), _("States")]
    model = State
