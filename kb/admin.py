# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Administrative interface for KB application
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.contrib import admin
from django import forms
from noc.kb.models import *

##
## Admin for Categories
##
class KBCategoryAdmin(admin.ModelAdmin):
    list_display=["name"]
##
## Inline Admin for Attachments
##
class KBEntryAttachmentForm(forms.ModelForm):
    class Meta:
        model=KBEntryAttachment

class KBEntryAttachmentAdmin(admin.TabularInline):
    form=KBEntryAttachmentForm
    model=KBEntryAttachment
    extra=3
##
## Admin for Entries
##
class KBEntryAdmin(admin.ModelAdmin):
    list_display=["id","subject","view_link"]
    search_fields=["id","subject"]
    inlines=[KBEntryAttachmentAdmin]
    def save_model(self, request, obj, form, change):
        obj.save(user=request.user)

##
## Register administrative interfaces
##
admin.site.register(KBCategory, KBCategoryAdmin)
admin.site.register(KBEntry,    KBEntryAdmin)
