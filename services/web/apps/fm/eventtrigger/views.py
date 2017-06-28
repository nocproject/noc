# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.eventtrigger application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.fm.models.eventtrigger import EventTrigger
from noc.core.translation import ugettext as _


class EventTriggerApplication(ExtModelApplication):
    """
    EventTrigger application
    """
    title = _("Event Triggers")
    menu = [_("Setup"), _("Event Triggers")]
    model = EventTrigger
