# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TaskSchedule Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.sa.models import TaskSchedule
import datetime
##
## TaskSchedule admin
##
class TaskScheduleAdmin(admin.ModelAdmin):
    list_display=["periodic_name","is_enabled","run_every","next_run"]
    search_fields=["periodic_name"]
    actions=["run_now"]
    list_editable=["is_enabled","run_every"]
    list_filter=["is_enabled"]
    ##
    ## Reschedule selected tasks
    ##
    def run_now(self,request,queryset):
        updated=0
        now=datetime.datetime.now()
        for t in queryset:
            t.next_run=now
            t.save()
            updated+=1
        if updated==1:
            message="1 task rescheduled"
        else:
            message="%d tasks rescheduled"%updated
        self.message_user(request,message)
    run_now.short_description="Run selected tasks now"
##
## TaskSchedule application
##
class TaskScheduleApplication(ModelApplication):
    model=TaskSchedule
    model_admin=TaskScheduleAdmin
    menu="Task Schedules"
