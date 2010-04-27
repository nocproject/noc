# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventClass Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.fm.models import EventClass,EventClassVar

##
## Variable inlines
##
class EventClassVarAdmin(admin.TabularInline):
    extra=5
    model=EventClassVar
##
## EventClass admin
##
class EventClassAdmin(admin.ModelAdmin):
    list_display=["name","category","default_priority","is_builtin","repeat_suppression","repeat_suppression_interval",
        "trigger","last_modified","python_link"]
    search_fields=["name"]
    list_filter=["is_builtin","category"]
    inlines=[EventClassVarAdmin]
##
## EventClass application
##
class EventClassApplication(ModelApplication):
    model=EventClass
    model_admin=EventClassAdmin
    menu="Setup | Event Classes"
