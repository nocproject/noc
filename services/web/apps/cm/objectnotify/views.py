# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectNotify Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.cm.models import ObjectNotify
##
## ObjectNotify admin
##
class ObjectNotifyAdmin(admin.ModelAdmin):
    list_display=["type","administrative_domain","notify_immediately","notify_delayed","notification_group"]
    list_filter=["type","administrative_domain","notification_group"]
##
## ObjectNotify application
##
class ObjectNotifyApplication(ModelApplication):
    model=ObjectNotify
    model_admin=ObjectNotifyAdmin
    menu="Setup | Object Notifies"
