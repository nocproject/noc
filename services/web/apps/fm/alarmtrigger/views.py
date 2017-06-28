# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.alarmtrigger application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.fm.models.alarmtrigger import AlarmTrigger
from noc.core.translation import ugettext as _


class AlarmTriggerApplication(ExtModelApplication):
    """
    AlarmTrigger application
    """
    title = _("Alarm Triggers")
    menu = [_("Setup"), _("Alarm Triggers")]
    model = AlarmTrigger
