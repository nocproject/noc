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
from noc.lib.render import render
from noc.lib.admin_actions import enable_selected,disable_selected
from noc.lib.fileutils import in_dir
from noc.settings import config
import os,datetime

class ActivatorAdmin(admin.ModelAdmin):
    list_display=["name","ip","is_active"]
    
class TaskScheduleAdmin(admin.ModelAdmin):
    list_display=["periodic_name","is_enabled","run_every","next_run"]
    search_fields=["periodic_name"]
    actions=["run_now",enable_selected,disable_selected]
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

class AdministrativeDomainAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    search_fields=["name","description"]

class ObjectGroupAdmin(admin.ModelAdmin):
    list_display=["name","description"]
    search_fields=["name","description"]

class ManagedObjectAdminForm(forms.ModelForm):
    class Meta:
        model=ManagedObject
    def clean_scheme(self):
        if "profile_name" not in self.cleaned_data:
            return self.cleaned_data["scheme"]
        profile=profile_registry[self.cleaned_data["profile_name"]]
        if self.cleaned_data["scheme"] not in profile.supported_schemes:
            raise forms.ValidationError("Selected scheme is not supported for profile '%s'"%self.cleaned_data["profile_name"])
        return self.cleaned_data["scheme"]
    # Check repo_path remains inside repo
    def clean_repo_path(self):
        repo=os.path.join(config.get("cm","repo"),"config")
        if self.cleaned_data["repo_path"] and self.cleaned_data["repo_path"].startswith("."):
            raise forms.ValidationError("Invalid repo path")
        if not in_dir(os.path.join(repo,self.cleaned_data["repo_path"]),repo) or self.cleaned_data["repo_path"].startswith(os.sep):
            raise forms.ValidationError("Repo path must be relative path inside repo")
        return os.path.normpath(self.cleaned_data["repo_path"])
        
class ManagedObjectAdmin(admin.ModelAdmin):
    form=ManagedObjectAdminForm
    fieldsets=(
        (None,{
            "fields": ("name","is_managed","administrative_domain","activator","profile_name","description")
        }),
        ("Access",{
            "fields": ("scheme","address","port","remote_path")
        }),
        ("Credentials",{
            "fields": ("user","password","super_password")
        }),
        ("SNMP",{
            "fields": ("snmp_ro","snmp_rw","trap_source_ip","trap_community")
        }),
        ("CM",{
            "fields": ("is_configuration_managed","repo_path")
        }),
        ("Groups", {
            "fields": ("groups",)
        }),
    )
    list_display=["name","is_managed","profile_name","address","administrative_domain","activator","is_configuration_managed","description","repo_path","action_links"]
    list_filter=["is_managed","is_configuration_managed","activator","administrative_domain","groups","profile_name"]
    search_fields=["name","address","repo_path","description"]
    object_class=ManagedObject
    ##
    ## Dirty hack to display PasswordInput in admin form
    ##
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in ["password","super_password"]:
            kwargs["widget"]=forms.widgets.PasswordInput
            if "request" in kwargs: # For Django 1.1 compatibility
                kwargs.pop("request",None)
            return db_field.formfield(**kwargs)
        return super(ManagedObjectAdmin,self).formfield_for_dbfield(db_field,**kwargs)
    ##
    ## Row-level access control
    ##
    def has_change_permission(self,request,obj=None):
        if obj:
            return obj.has_access(request.user)
        else:
            return admin.ModelAdmin.has_delete_permission(self,request)
            
    def has_delete_permission(self,request,obj=None):
        return self.has_change_permission(request,obj)
        
    def queryset(self,request):
        return ManagedObject.queryset(request.user)
        
    def save_model(self, request, obj, form, change):
        if obj.can_change(request.user,form.cleaned_data["administrative_domain"],form.cleaned_data["groups"]):
            admin.ModelAdmin.save_model(self,request,obj,form,change)
        else:
            raise "Permission denied"

class UserAccessAdmin(admin.ModelAdmin):
    list_display=["user","administrative_domain","group"]
    list_filter=["user","administrative_domain","group"]

##
##
##
class ManagedObjectSelectorAdmin(admin.ModelAdmin):
    list_display=["name","is_enabled"]
    list_filter=["is_enabled"]
    actions=["test_selectors"]
    ##
    ## Test selected seletors
    ##
    def test_selectors(self,request,queryset):
        r=[{"name":q.name,"objects":q.managed_objects} for q in queryset]
        return render(request,"sa/test_selector.html",{"data":r})
    test_selectors.short_description="Test Selectors"

admin.site.register(Activator,            ActivatorAdmin)
admin.site.register(AdministrativeDomain, AdministrativeDomainAdmin)
admin.site.register(ObjectGroup,          ObjectGroupAdmin)
admin.site.register(ManagedObject,        ManagedObjectAdmin)
admin.site.register(UserAccess,           UserAccessAdmin)
admin.site.register(TaskSchedule,         TaskScheduleAdmin)
admin.site.register(ManagedObjectSelector, ManagedObjectSelectorAdmin)
