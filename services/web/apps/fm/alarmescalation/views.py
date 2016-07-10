# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.alarmescalation application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models.alarmescalation import AlarmEscalation


class AlarmEscalationApplication(ExtDocApplication):
    """
    AlarmEscalation application
    """
    title = "Alarm Escalation"
    menu = "Setup | Alarm Escalation"
    model = AlarmEscalation
