# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NotificationGroup Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.main.models import NotificationGroup,NotificationGroupUser,NotificationGroupOther
##
## Notification Groups Admin
##
class NotificationGroupUserAdmin(admin.TabularInline):
    extra=5
    model=NotificationGroupUser

class NotificationGroupOtherAdmin(admin.TabularInline):
    extra=5
    model=NotificationGroupOther

class NotificationGroupAdmin(admin.ModelAdmin):
    list_display=["name"]
    search_fields=["name"]
    inlines=[NotificationGroupUserAdmin,NotificationGroupOtherAdmin]
##
## NotificationGroup application
##
class NotificationGroupApplication(ModelApplication):
    model=NotificationGroup
    model_admin=NotificationGroupAdmin
    menu="Setup | Notification Groups"
