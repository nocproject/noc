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
        "rule","last_modified"]
    search_fields=["name"]
    list_filter=["is_builtin","category"]
    inlines=[EventClassVarAdmin]
    actions=["view_python"]
    ##
    ## Display python code for selected objects
    ##
    def view_python(self,request,queryset):
        code="\n\n".join([o.python_code for o in queryset])
        return self.app.render_plain_text(code)
    view_python.short_description="View Python Code for selected objects"
##
## EventClass application
##
class EventClassApplication(ModelApplication):
    model=EventClass
    model_admin=EventClassAdmin
    menu="Setup | Event Classes"
