# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Schedule Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication
from noc.main.models import Schedule
from noc.lib.periodic import periodic_registry
##
## Schedule admin
##
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ["periodic_name", "is_enabled", "time_pattern",
                    "run_every", "timeout", "last_run", "last_status"]
    search_fields = ["periodic_name"]
    actions = ["run_now"]
    list_editable = ["is_enabled","run_every", "timeout"]
    list_filter = ["is_enabled"]
    ##
    ## Reschedule selected tasks
    ##
    def run_now(self, request, queryset):
        updated = 0
        now = datetime.datetime.now()
        for t in queryset:
            t.last_run = now - datetime.timedelta(seconds=t.run_every)
            t.save()
            updated += 1
        if updated==1:
            message = "1 task has been rescheduled"
        else:
            message = "%d tasks have been rescheduled" % updated
        self.message_user(request, message)
    run_now.short_description="Run selected tasks now"
    ##
    ## Handle timeout
    ##
    def save_model(self, request, obj, form, change):
        if obj.periodic_name:
            t = periodic_registry[obj.periodic_name].default_timeout
            if not t:
                obj.timeout = None
        return super(ScheduleAdmin, self).save_model(request, obj, form, change)
    

##
## Schedule application
##
class ScheduleApplication(ModelApplication):
    model=Schedule
    model_admin=ScheduleAdmin
    menu="Setup | Schedules"
