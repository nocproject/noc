# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventClassificationRule Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django.shortcuts import get_object_or_404
from noc.lib.app import ModelApplication,HasPerm
from noc.fm.models import Event,EventClassificationRule,EventClassificationRE
##
## Inline for EventClassificationRE
##
class EventClassificationREAdmin(admin.TabularInline):
    extra=3
    model=EventClassificationRE
##
## EventClassificationRule admin
##
class EventClassificationRuleAdmin(admin.ModelAdmin):
    list_display=["name","event_class","preference","is_builtin","action"]
    search_fields=["name"]
    list_filter=["is_builtin","action","event_class"]
    inlines=[EventClassificationREAdmin]
    actions=["view_python"]
    ##
    ## Display python code for selected objects
    ##
    def view_python(self,request,queryset):
        code="\n\n".join([o.python_code for o in queryset])
        return self.app.render_plain_text(code)
    view_python.short_description="View Python Code for selected objects"
##
## EventClassificationRule application
##
class EventClassificationRuleApplication(ModelApplication):
    model=EventClassificationRule
    model_admin=EventClassificationRuleAdmin
    menu="Setup | Classification Rules"
    ##
    ## Clone existing rule
    ##
    def view_clone(self,request,object_id):
        rule=get_object_or_404(EventClassificationRule,id=int(object_id))
        new_rule=rule.clone()
        self.message_user(request,"Rule cloned")
        return self.response_redirect_to_object(new_rule)
    view_clone.url=r"^(?P<object_id>\d+)/clone/"
    view_clone.url_name="clone"
    view_clone.access=HasPerm("add")
    ##
    ## Create rule from event
    ##
    def view_from_event(self,request,event_id):
        event=get_object_or_404(Event,id=int(event_id))
        rule=EventClassificationRule.from_event(event)
        self.message_user(request,"Rule created from event")
        return self.response_redirect_to_object(rule)
    view_from_event.url=r"^from_event/(?P<event_id>\d+)/$"
    view_from_event.url_name="from_event"
    view_from_event.access=HasPerm("add")
