# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# wf.transition application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.wf.models.transition import Transition
from noc.core.translation import ugettext as _


class TransitionApplication(ExtDocApplication):
    """
    Transition application
    """
    title = "Transitions"
    menu = [_("Setup"), _("Transitions")]
    model = Transition
