# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.contrib import admin
from django import forms
from models import *
##
class MIBDataInlineAdmin(admin.TabularInline):
    model=MIBData
    extra=0
##
class MIBAdmin(admin.ModelAdmin):
    list_display=["name","last_updated","uploaded"]
    search_fields=["name"]
    inlines=[MIBDataInlineAdmin]
##
class MIBDataAdmin(admin.ModelAdmin):
    list_display=["mib","oid","name"]
    search_fields=["oid","name"]
##
class EventPriorityAdmin(admin.ModelAdmin):
    list_display=["name","priority"]
    search_fields=["name"]
##
class EventCategoryAdmin(admin.ModelAdmin):
    list_display=["name"]
    search_fields=["name"]
##
class EventClassVarAdmin(admin.TabularInline):
    extra=5
    model=EventClassVar
##
class EventClassAdmin(admin.ModelAdmin):
    list_display=["name","category","default_priority","is_builtin","repeat_suppression","repeat_suppression_interval",
        "trigger","last_modified","python_link"]
    search_fields=["name"]
    list_filter=["is_builtin","category"]
    inlines=[EventClassVarAdmin]
##
class EventClassificationREAdmin(admin.TabularInline):
    extra=3
    model=EventClassificationRE
##
class EventClassificationRuleAdmin(admin.ModelAdmin):
    list_display=["name","event_class","preference","is_builtin","action","python_link"]
    search_fields=["name"]
    list_filter=["is_builtin","action","event_class"]
    inlines=[EventClassificationREAdmin]
##
## Inline for EventPostProcessingRuleAdmin
##
class EventPostProcessingREAdmin(admin.TabularInline):
    extra=3
    model=EventPostProcessingRE
##
##
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
##
##
class EventCorrelationMatchedClassAdmin(admin.TabularInline):
    extra=3
    model=EventCorrelationMatchedClass
##
##
##
class EventCorrelationMatchedVarAdmin(admin.TabularInline):
    extra=3
    model=EventCorrelationMatchedVar
##
##
##
class EventCorrelationRuleAdmin(admin.ModelAdmin):
    list_display=["name","is_builtin","python_link"]
    search_fields=["name"]
    list_filter=["is_builtin"]
    inlines=[EventCorrelationMatchedClassAdmin,EventCorrelationMatchedVarAdmin]
##
##
##
class EventArchivationRuleAdmin(admin.ModelAdmin):
    list_display=["event_class","ttl","ttl_measure","action"]
    list_filter=["action","event_class"]
##
admin.site.register(MIB, MIBAdmin)
admin.site.register(MIBData, MIBDataAdmin)
admin.site.register(EventPriority, EventPriorityAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(EventClass, EventClassAdmin)
admin.site.register(EventClassificationRule, EventClassificationRuleAdmin)
admin.site.register(EventPostProcessingRule, EventPostProcessingRuleAdmin)
admin.site.register(EventCorrelationRule, EventCorrelationRuleAdmin)
admin.site.register(EventArchivationRule, EventArchivationRuleAdmin)