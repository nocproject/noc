# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Notification Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.main.models import Notification
##
## Notification Admin
##
class NotificationAdmin(admin.ModelAdmin):
    list_display=["timestamp","notification_method","notification_params","subject","next_try"]

##
## Notification application
##
class NotificationApplication(ModelApplication):
    model=Notification
    model_admin=NotificationAdmin
    menu="Setup | Pending Notifications"
