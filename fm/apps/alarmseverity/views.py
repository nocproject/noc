# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.alarmseverity application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import AlarmSeverity


class AlarmSeverityApplication(ExtDocApplication):
    """
    AlarmSeverity application
    """
    title = "Alarm Severity"
    menu = "Setup | Alarm Severities"
    model = AlarmSeverity

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""
