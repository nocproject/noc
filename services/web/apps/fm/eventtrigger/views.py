# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.eventtrigger application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.fm.models.eventtrigger import EventTrigger
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication


class EventTriggerApplication(ExtModelApplication):
    """
    EventTrigger application
    """
    title = _("Event Triggers")
    menu = [_("Setup"), _("Event Triggers")]
    model = EventTrigger
