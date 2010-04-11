# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Administrative interface for Main application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.contrib import admin
from django import forms
from django.forms.models import modelform_factory
from django.core import serializers
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from noc.main.models import *
from noc.lib.render import render

##
## Global admin actions
##
##
## Export selected objects as XML
##
def xml_export(modeladmin,request,queryset):
    response=HttpResponse(mimetype="text/xml")
    serializers.serialize('xml',queryset,stream=response)
    return response
xml_export.short_description="Export selected objects as XML"
##
## Bulk field change
## (Not working)
def bulk_change(modeladmin,request,queryset):
    model=modeladmin.model
    form_class=modelform_factory(model)
    for f in model._meta.fields:
        if f.name not in form_class.base_fields:
            continue
        # Remove unique and auto fields
        if f.unique or f.auto_created:
            del form_class.base_fields[f.name]
    context={
        'add':    False,
        'change': True,
        'has_add_permission':    modeladmin.has_add_permission(request),
        'has_change_permission': modeladmin.has_change_permission(request),
        'has_delete_permission': modeladmin.has_delete_permission(request),
        'has_file_field': False,
        'has_absolute_url': hasattr(model, 'get_absolute_url'),
        'ordered_objects': None,
        'form_url': "",
        'opts': model._meta,
        'content_type_id': ContentType.objects.get_for_model(model).id,
        'save_as': modeladmin.save_as,
        'save_on_top': modeladmin.save_on_top,
        'root_path': modeladmin.admin_site.root_path,
        'is_popup' : False,
        'adminform': form_class(),
        'title': "Bulk Change",
        'adminform': modeladmin.form,
    }
    print dir(modeladmin)
    return render(request,"main/bulk_change.html",context)
#bulk_change.short_description="Bulk field change"

##
##
##
class AuditTrailAdmin(admin.ModelAdmin):
    list_display=["user","timestamp","model","db_table","operation","subject"]
    list_filter=["user"]
##
## Admin for Language
##
class LanguageAdmin(admin.ModelAdmin):
    list_display=["name","native_name","is_active"]
    search_fields=["name","native_name"]
    list_filter=["is_active"]
##
## Admin for MIME Types
##
class MIMETypeAdmin(admin.ModelAdmin):
    list_display=["extension","mime_type"]
    search_fields=["extension","mime_type"]
##
## Admin for pyRules
##
class PyRuleForm(forms.ModelForm):
    class Meta:
        model=PyRule
    def clean_text(self):
        text=self.cleaned_data["text"]
        try:
            PyRule.compile_text(text)
        except SyntaxError,why:
            raise forms.ValidationError("Syntax Error: "+str(why))
        return text.replace("\r\n","\n")

class PyRuleAdmin(admin.ModelAdmin):
    form=PyRuleForm
    list_display=["name","interface"]
    search_fields=["name"]

##
class RefBookFieldAdmin(admin.TabularInline):
    extra=3
    model=RefBookField
##
## Admin for Ref Books
##
class RefBookAdmin(admin.ModelAdmin):
    list_display=["name","is_builtin","is_enabled"]
    search_fields=["name"]
    list_filter=["is_enabled","is_builtin"]
    inlines=[RefBookFieldAdmin]
##
## Admin for Time Patterns
##
class TimePatternTermForm(forms.ModelForm):
    class Meta:
        model=TimePatternTerm
    def clean_term(self):
        try:
            TimePatternTerm.check_syntax(self.cleaned_data["term"])
        except SyntaxError,why:
            raise forms.ValidationError(why)
        return self.cleaned_data["term"]
    
class TimePatternTermAdmin(admin.TabularInline):
    extra=5
    model=TimePatternTerm
    form=TimePatternTermForm
    
class TimePatternAdmin(admin.ModelAdmin):
    list_display=["name","test_link"]
    search_fields=["name"]
    inlines=[TimePatternTermAdmin]
    actions=["test_time_patterns"]
    ##
    ## Test Selected Time Patterns
    ##
    def test_time_patterns(self,request,queryset):
        return HttpResponseRedirect("/main/time_pattern/test/%s/"%",".join([str(p.id) for p in queryset]))
    test_time_patterns.short_description="Test Selected Time Patterns"
    
##
## Notification Groups Admin
##
class NotificationGroupUserAdmin(admin.TabularInline):
    extra=5
    model=NotificationGroupUser

class NotificationGroupOtherAdmin(admin.TabularInline):
    extra=5
    model=NotificationGroupOther

class NotificationGroupAdmin(admin.ModelAdmin):
    list_display=["name"]
    search_fields=["name"]
    inlines=[NotificationGroupUserAdmin,NotificationGroupOtherAdmin]
##
## Notification Admin
##
class NotificationAdmin(admin.ModelAdmin):
    list_display=["timestamp","notification_method","notification_params","subject","next_try"]
##
## UserProfile Admin
##
class UserProfileContactAdmin(admin.TabularInline):
    extra=5
    model=UserProfileContact
    
class UserProfileAdmin(admin.ModelAdmin):
    inlines=[UserProfileContactAdmin]
    fieldsets=(
        (None, {
            "fields" : ("preferred_language",),
        }),
    )

##
## System Notification Admin
##
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display=["name","notification_group"]
##
## Register default actions
##
admin.site.add_action(bulk_change)
admin.site.add_action(xml_export)
##
## Register administrative interfaces
##
admin.site.register(AuditTrail, AuditTrailAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(MIMEType, MIMETypeAdmin)
admin.site.register(PyRule, PyRuleAdmin)
admin.site.register(RefBook, RefBookAdmin)
admin.site.register(TimePattern, TimePatternAdmin)
admin.site.register(NotificationGroup, NotificationGroupAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(SystemNotification, SystemNotificationAdmin)
