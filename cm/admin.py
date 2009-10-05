# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""

from django.contrib import admin
from django import forms
from noc.cm.models import ObjectNotify,Config,DNS,PrefixList,RPSL
from noc.sa.profiles import profile_registry

class ObjectNotifyAdmin(admin.ModelAdmin):
    list_display=["type","group","administrative_domain","notify_immediately","notify_delayed","notification_group"]
    list_filter=["type","group","administrative_domain","notification_group"]

class ObjectAdmin(admin.ModelAdmin):
    object_class=None
    fields=["pull_every"]

class ConfigAdmin(ObjectAdmin):
    list_display=["repo_path","pull_every","last_modified","next_pull","pull_now_link","view_link"]
    search_fields=["repo_path"]
    fields=["pull_every","next_pull"]
    object_class=Config
    def has_change_permission(self,request,obj=None):
        if obj:
            return obj.has_access(request.user)
        else:
            return admin.ModelAdmin.has_delete_permission(self,request)
            
    def has_delete_permission(self,request,obj=None):
        return self.has_change_permission(request,obj)
        
    def queryset(self,request):
        return self.object_class.queryset(request.user)
        
    def save_model(self, request, obj, form, change):
        if obj.has_access(request.user):
            admin.ModelAdmin.save_model(self,request,obj,form,change)
        else:
            raise "Permission denied"
    
    
class DNSAdmin(ObjectAdmin):
    list_display=["repo_path","last_modified","view_link"]
    search_fields=["repo_path"]
    object_class=DNS
    
class PrefixListAdmin(ObjectAdmin):
    list_display=["repo_path","last_modified","view_link"]
    search_fields=["repo_path"]
    object_class=PrefixList
    
class RPSLAdmin(ObjectAdmin):
    list_display=["repo_path","last_modified","view_link"]
    search_fields=["repo_path"]
    object_class=RPSL

admin.site.register(ObjectNotify,   ObjectNotifyAdmin)
admin.site.register(Config,         ConfigAdmin)
admin.site.register(DNS,            DNSAdmin)
admin.site.register(PrefixList,     PrefixListAdmin)
admin.site.register(RPSL,           RPSLAdmin)

