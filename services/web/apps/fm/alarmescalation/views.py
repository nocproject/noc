# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# fm.alarmescalation application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.fm.models.alarmescalation import AlarmEscalation
from noc.core.translation import ugettext as _


class AlarmEscalationApplication(ExtDocApplication):
    """
    AlarmEscalation application
    """
    title = _("Alarm Escalation")
    menu = [_("Setup"), _("Alarm Escalation")]
    model = AlarmEscalation
