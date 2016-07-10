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
from django import forms
## NOC modules
from noc.lib.app import ModelApplication
from noc.main.models import Schedule, PyRule
from noc.lib.periodic import periodic_registry


class ScheduleAdminForm(forms.ModelForm):
    class Meta:
        model = Schedule

    periodic_name = forms.ChoiceField(label="Periodic Task", choices=())

    def __init__(self, *args, **kwargs):
        super(ScheduleAdminForm, self).__init__(*args, **kwargs)
        c = [("Builtin", periodic_registry.choices)]
        prc = list(PyRule.objects.filter(interface="IPeriodicTask").order_by("name"))
        if prc:
            c += [("pyRule", [("pyrule:%s" % x, x) for x in prc])]
        self.fields["periodic_name"].choices = c


class ScheduleAdmin(admin.ModelAdmin):
    """
    Schedule admin
    """
    form = ScheduleAdminForm
    list_display = ["periodic_name", "is_enabled", "time_pattern",
                    "run_every", "timeout", "last_run", "last_status"]
    search_fields = ["periodic_name"]
    actions = ["run_now"]
    list_editable = ["is_enabled", "run_every", "timeout"]
    list_filter = ["is_enabled"]

    def run_now(self, request, queryset):
        """
        Reschedule selected tasks
        """
        updated = 0
        now = datetime.datetime.now()
        for t in queryset:
            t.last_run = now - datetime.timedelta(seconds=t.run_every)
            t.save()
            updated += 1
        if updated == 1:
            message = "1 task has been rescheduled"
        else:
            message = "%d tasks have been rescheduled" % updated
        self.message_user(request, message)
    run_now.short_description = "Run selected tasks now"

    def save_model(self, request, obj, form, change):
        """
        Handle timeout
        """
        if obj.periodic_name and not obj.periodic_name.startswith("pyrule:"):
            t = periodic_registry[obj.periodic_name].default_timeout
            if not t:
                obj.timeout = None
        return super(ScheduleAdmin, self).save_model(request, obj, form, change)


class ScheduleApplication(ModelApplication):
    """
    Schedule application
    """
    model = Schedule
    model_admin = ScheduleAdmin
    menu = "Setup | Schedules"
