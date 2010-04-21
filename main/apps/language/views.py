# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Language Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.contrib import admin
from noc.lib.app import ModelApplication
from noc.main.models import Language
##
## Admin for Language
##
class LanguageAdmin(admin.ModelAdmin):
    list_display=["name","native_name","is_active"]
    search_fields=["name","native_name"]
    list_filter=["is_active"]
##
##
##
class LanguageApplication(ModelApplication):
    model=Language
    model_admin=LanguageAdmin
    menu="Setup | Languages"
