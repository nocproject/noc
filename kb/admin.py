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
from noc.kb.models import *

##
## Admin for Categories
##
class KBCategoryAdmin(admin.ModelAdmin):
    list_display=["name"]
##
## Admin for Entries
##
class KBEntryAdmin(admin.ModelAdmin):
    list_display=["id","subject","view_link"]
    search_fields=["id","subject"]
    def save_model(self, request, obj, form, change):
        admin.ModelAdmin.save_model(self,request,obj,form,change)
        KBEntryHistory(kb_entry=obj,user=request.user,diff="zhopa").save()

##
## Register administrative interfaces
##
admin.site.register(KBCategory, KBCategoryAdmin)
admin.site.register(KBEntry,    KBEntryAdmin)
