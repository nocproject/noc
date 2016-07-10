# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.alarmclassconfig application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models.alarmclassconfig import AlarmClassConfig


class AlarmClassConfigApplication(ExtDocApplication):
    """
    AlarmClassConfig application
    """
    title = "Alarm Class Config"
    menu = "Setup | Alarm Class Config"
    model = AlarmClassConfig
