# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventPostProcessingRule Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django.shortcuts import get_object_or_404
from noc.lib.app import ModelApplication,HasPerm
from noc.fm.models import Event,EventPostProcessingRule,EventPostProcessingRE
##
## Inline for EventPostProcessingRuleAdmin
##
class EventPostProcessingREAdmin(admin.TabularInline):
    extra=3
    model=EventPostProcessingRE
##
## EventPostProcessingRule admin
##
class EventPostProcessingRuleAdmin(admin.ModelAdmin):
    fieldsets=(
        (None,{
            "fields": ("name","event_class","preference","is_active","description","time_pattern","managed_object_selector")}
        ),
        ("Action",{
            "fields": ("action","change_priority","change_category","notification_group","rule")
        }),
    )
    list_display=["name","event_class","preference","is_active","action","change_priority","change_category","rule"]
    search_fields=["name"]
    list_filter=["is_active","event_class"]
    inlines=[EventPostProcessingREAdmin]
##
## EventPostProcessingRule application
##
class EventPostProcessingRuleApplication(ModelApplication):
    model=EventPostProcessingRule
    model_admin=EventPostProcessingRuleAdmin
    menu="Setup | Post-Processing Rules"
    ##
    ## Clone existing rule
    ##
    def view_clone(self,request,object_id):
        rule=get_object_or_404(EventPostProcessingRule,id=int(object_id))
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
        rule=EventPostProcessingRule.from_event(event)
        self.message_user(request,"Rule created from event")
        return self.response_redirect_to_object(rule)
    view_from_event.url=r"^from_event/(?P<event_id>\d+)/$"
    view_from_event.url_name="from_event"
    view_from_event.access=HasPerm("add")
