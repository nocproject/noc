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

class EventClassVarAdmin(admin.TabularInline):
    extra=1
    model=EventClassVar
    
class EventClassAdmin(admin.ModelAdmin):
    list_display=["name","category","default_priority","repeat_suppression","repeat_suppression_interval","last_modified"]
    search_fields=["name"]
    inlines=[EventClassVarAdmin]
#class EventClassVarAdmin(admin.ModelAdmin):
#    list_display=["event_class","name","required","repeat_suppression"]
#    list_filter=["event_class"]

class EventClassificationREAdmin(admin.TabularInline):
    extra=3
    model=EventClassificationRE

class EventClassificationRuleAdmin(admin.ModelAdmin):
    list_display=["event_class","name","preference","drop_event"]
    search_fields=["name"]
    list_filter=["event_class","drop_event"]
    inlines=[EventClassificationREAdmin]

admin.site.register(MIB, MIBAdmin)
admin.site.register(MIBData, MIBDataAdmin)
admin.site.register(EventPriority, EventPriorityAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(EventClass, EventClassAdmin)
#admin.site.register(EventClassVar, EventClassVarAdmin)
admin.site.register(EventClassificationRule, EventClassificationRuleAdmin)
