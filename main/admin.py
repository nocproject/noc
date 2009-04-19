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
from noc.main.models import *

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
## Register administrative interfaces
##
admin.site.register(Language, LanguageAdmin)
admin.site.register(MIMEType, MIMETypeAdmin)
