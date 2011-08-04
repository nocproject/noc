# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventTrigger Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import re
## Django modules
from django.contrib import admin
## NOC modules
from noc.lib.app import ModelApplication, view, HasPerm
from noc.fm.models import EventTrigger, EventClass


class EventTriggerAdmin(admin.ModelAdmin):
    list_display = ["name", "is_enabled", "event_class_re", "condition",
            "time_pattern", "selector", "notification_group",
            "template", "pyrule"]
    list_filter = ["is_enabled"]
    actions = ["test_triggers"]

    def test_triggers(self, request, queryset):
        return self.app.response_redirect("test/%s/" % ",".join(
                                                [str(p.id) for p in queryset]))
    test_triggers.short_description = "Test selected triggers"


class EventTriggerApplication(ModelApplication):
    model = EventTrigger
    model_admin = EventTriggerAdmin
    menu = "Setup | Event Triggers"

    @view(url=r"^test/(?P<objects>\d+(?:,\d+)*)/$",
          url_name="test", access=HasPerm("change"))
    def view_test(self, request, objects):
        ecn = sorted([c.name for c in EventClass.objects.all()])
        r = []
        for o_id in objects.split(","):
            t = self.get_object_or_404(EventTrigger, id=int(o_id))
            rx = re.compile(t.event_class_re)
            r += [{
                    "trigger": t,
                    "classes": [c for c in ecn if rx.search(c) is not None]
                }]
        return self.render(request, "test.html", r=r)
