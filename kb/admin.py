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
## Admin for Global Bookmarks
##
class KBGlobalBookmarkAdmin(admin.ModelAdmin):
    list_display=["kb_entry"]
##
## Admin for User Bookmarks
##
class UserBookmarksAdmin(admin.ModelAdmin):
    def queryset(self,request):
        return KBUserBookmark.objects.filter(user=request.user)

    def has_change_permission(self,request,obj=None):
        if obj:
            return obj.has_access(request.user)
        else:
            return admin.ModelAdmin.has_delete_permission(self,request)

    def has_delete_permission(self,request,obj=None):
        return self.has_change_permission(request,obj)
##
##
##
class KBEntryTemplateAdmin(admin.ModelAdmin):
    list_display=["name","subject"]
##
## Register administrative interfaces
##
admin.site.register(KBCategory, KBCategoryAdmin)
admin.site.register(KBEntry,    KBEntryAdmin)
admin.site.register(KBGlobalBookmark, KBGlobalBookmarkAdmin)
admin.site.register(KBEntryTemplate, KBEntryTemplateAdmin)
