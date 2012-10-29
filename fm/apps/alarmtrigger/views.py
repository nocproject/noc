# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.alarmtrigger application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.fm.models import AlarmTrigger


class AlarmTriggerApplication(ExtModelApplication):
    """
    AlarmTrigger application
    """
    title = "Alarm Triggers"
    menu = "Setup | Alarm Triggers"
    model = AlarmTrigger
