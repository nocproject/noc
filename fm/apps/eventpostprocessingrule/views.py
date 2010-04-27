# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EventPostProcessingRule Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.fm.models import EventPostProcessingRule,EventPostProcessingRE
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
            "fields": ("action","change_priority","change_category","notification_group")
        }),
    )
    list_display=["name","event_class","preference","is_active","action","change_priority","change_category"]
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
