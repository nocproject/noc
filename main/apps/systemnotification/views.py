# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SystemNotification Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.main.models import SystemNotification
##
## System Notification Admin
##
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display=["name","notification_group"]
##
## SystemNotification application
##
class SystemNotificationApplication(ModelApplication):
    model=SystemNotification
    model_admin=SystemNotificationAdmin
    menu="Setup | System Notifications"
