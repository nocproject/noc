# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## KBEntry Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from django import forms
from noc.lib.app import ModelApplication
from noc.kb.models import KBEntry,KBEntryAttachment
##
## Inline Admin for Attachments
##
class KBEntryAttachmentForm(forms.ModelForm):
    class Meta:
        model=KBEntryAttachment
##
## Entry attacment admin
##
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
## KBEntry application
##
class KBEntryApplication(ModelApplication):
    model=KBEntry
    model_admin=KBEntryAdmin
    menu="Setup | Entries"
