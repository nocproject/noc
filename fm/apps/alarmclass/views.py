# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.alarmclass application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import AlarmClass


class AlarmClassApplication(ExtDocApplication):
    """
    AlarmClass application
    """
    title = "Alarm Class"
    menu = "Setup | Alarm Classes"
    model = AlarmClass
    query_fields = ["name", "description"]
    query_condition = "icontains"
