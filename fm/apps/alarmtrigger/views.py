# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmTrigger Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.fm.models import AlarmTrigger


class AlarmTriggerAdmin(admin.ModelAdmin):
    list_display = ["name", "is_enabled", "alarm_class_re", "condition",
            "time_pattern", "selector", "notification_group",
            "template", "pyrule"]
    list_filter = ["is_enabled"]


class AlarmTriggerApplication(ModelApplication):
    model = AlarmTrigger
    model_admin = AlarmTriggerAdmin
    menu = "Setup | Alarm Triggers"
