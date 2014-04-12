# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.alarmclass application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.alarmclasscategory import AlarmClassCategory


class AlarmClassApplication(ExtDocApplication):
    """
    AlarmClass application
    """
    title = "Alarm Class"
    menu = "Setup | Alarm Classes"
    model = AlarmClass
    parent_model = AlarmClassCategory
    parent_field = "parent"
    query_fields = ["name", "description"]
    query_condition = "icontains"

    def field_row_class(self, o):
        return o.default_severity.style.css_class_name
