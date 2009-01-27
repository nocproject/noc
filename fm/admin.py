from django.contrib import admin
from django import forms
from models import *

class MIBAdmin(admin.ModelAdmin):
    list_display=["name","last_updated","uploaded"]
    search_fields=["name"]

class MIBDataAdmin(admin.ModelAdmin):
    list_display=["mib","oid","name"]
    search_fields=["oid","name"]

class EventPriorityAdmin(admin.ModelAdmin):
    list_display=["name","priority"]
    search_fields=["name"]

class EventCategoryAdmin(admin.ModelAdmin):
    list_display=["name"]
    search_fields=["name"]

class EventClassAdmin(admin.ModelAdmin):
    list_display=["name","category","default_priority","last_modified"]
    search_fields=["name"]

class EventClassificationREAdmin(admin.TabularInline):
    extra=3
    model=EventClassificationRE
        
class EventClassificationRuleAdmin(admin.ModelAdmin):
    list_display=["event_class","name","preference"]
    search_fields=["name"]
    list_filter=["event_class"]
    inlines=[EventClassificationREAdmin]

admin.site.register(MIB, MIBAdmin)
admin.site.register(MIBData, MIBDataAdmin)
admin.site.register(EventPriority, EventPriorityAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(EventClass, EventClassAdmin)
admin.site.register(EventClassificationRule, EventClassificationRuleAdmin)
