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
from noc.main.models import *

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
##
## Register administrative interfaces
##
admin.site.register(AuditTrail, AuditTrailAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(MIMEType, MIMETypeAdmin)
admin.site.register(RefBook, RefBookAdmin)
admin.site.register(TimePattern, TimePatternAdmin)
