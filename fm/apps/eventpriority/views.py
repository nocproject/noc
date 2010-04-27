# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventPriority Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.fm.models import EventPriority
##
## EventPriority admin
##
class EventPriorityAdmin(admin.ModelAdmin):
    list_display=["name","priority"]
    search_fields=["name"]
##
## EventPriority application
##
class EventPriorityApplication(ModelApplication):
    model=EventPriority
    model_admin=EventPriorityAdmin
    menu="Setup | Event Priorities"
